"""
ModpackService for CurseForge API integration.

This service handles modpack search, details, and version retrieval from the CurseForge API
with caching, rate limiting, and comprehensive error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ModpackSearchResult(BaseModel):
    """Modpack search result model."""
    id: int
    name: str
    summary: str
    download_count: int
    categories: List[str] = Field(default_factory=list)
    authors: List[str] = Field(default_factory=list)
    logo_url: Optional[str] = None
    last_updated: Optional[datetime] = None


class ModpackDetails(BaseModel):
    """Detailed modpack information model."""
    id: int
    name: str
    summary: str
    description: str
    download_count: int
    categories: List[str] = Field(default_factory=list)
    authors: List[str] = Field(default_factory=list)
    logo_url: Optional[str] = None
    screenshots: List[str] = Field(default_factory=list)
    last_updated: Optional[datetime] = None
    game_version_latest: Optional[str] = None
    mod_loader: Optional[str] = None


class ModpackVersion(BaseModel):
    """Modpack version information model."""
    id: int
    display_name: str
    file_name: str
    file_date: datetime
    download_url: str
    game_versions: List[str] = Field(default_factory=list)
    mod_loader: Optional[str] = None
    file_size: int = 0


class CustomModpackSource(BaseModel):
    """Custom modpack source for direct URL or file upload."""
    name: str
    description: str = ""
    download_url: str
    file_name: str
    mod_loader: Optional[str] = None
    game_version: Optional[str] = None
    source_type: str = "custom"  # "url", "upload", "curseforge"


class CacheEntry:
    """Cache entry with expiration."""

    def __init__(self, data: Any, ttl_seconds: int = 300):
        self.data = data
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []

    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        # Remove old requests outside the window
        self.requests = [
            req_time for req_time in self.requests if now - req_time < self.window_seconds]

        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = self.window_seconds - (now - oldest_request)
            if wait_time > 0:
                logger.info(
                    f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)

        self.requests.append(now)


class ModpackServiceError(Exception):
    """Base exception for ModpackService errors."""
    pass


class APIConnectionError(ModpackServiceError):
    """Raised when API connection fails."""
    pass


class APIRateLimitError(ModpackServiceError):
    """Raised when API rate limit is exceeded."""
    pass


class ModpackNotFoundError(ModpackServiceError):
    """Raised when a modpack is not found."""
    pass


class ModpackService:
    """Service for interacting with the CurseForge API."""

    # CurseForge API endpoints
    BASE_URL = "https://api.curseforge.com/v1"
    MINECRAFT_GAME_ID = 432
    MODPACK_CATEGORY_ID = 4471

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ModpackService.

        Args:
            api_key: CurseForge API key (optional for public endpoints)
        """
        self.api_key = api_key
        self.cache: Dict[str, CacheEntry] = {}
        self.rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
        self.client = None

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "ContainerCraft/1.0"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key from endpoint and parameters."""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{endpoint}?{param_str}"

    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if not expired."""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                return entry.data
            else:
                del self.cache[cache_key]
        return None

    def _cache_data(self, cache_key: str, data: Any, ttl_seconds: int = 300):
        """Cache data with TTL."""
        self.cache[cache_key] = CacheEntry(data, ttl_seconds)

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the CurseForge API with error handling.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data

        Raises:
            APIConnectionError: When connection fails
            APIRateLimitError: When rate limited
            ModpackServiceError: For other API errors
        """
        if not self.client:
            raise ModpackServiceError(
                "Service not initialized. Use async context manager.")

        params = params or {}
        cache_key = self._get_cache_key(endpoint, params)

        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_data

        # Apply rate limiting
        await self.rate_limiter.acquire()

        try:
            response = await self.client.get(endpoint, params=params)

            if response.status_code == 429:
                raise APIRateLimitError("API rate limit exceeded")
            elif response.status_code == 404:
                raise ModpackNotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code >= 400:
                raise ModpackServiceError(
                    f"API error {response.status_code}: {response.text}")

            data = response.json()

            # Cache successful responses
            self._cache_data(cache_key, data, ttl_seconds=300)

            return data

        except httpx.ConnectError as e:
            raise APIConnectionError(
                f"Failed to connect to CurseForge API: {str(e)}")
        except httpx.TimeoutException as e:
            raise APIConnectionError(f"Request timeout: {str(e)}")
        except httpx.HTTPError as e:
            raise ModpackServiceError(f"HTTP error: {str(e)}")

    def _parse_modpack_search_result(self, mod_data: Dict[str, Any]) -> ModpackSearchResult:
        """Parse modpack data from search results."""
        return ModpackSearchResult(
            id=mod_data["id"],
            name=mod_data["name"],
            summary=mod_data.get("summary", ""),
            download_count=mod_data.get("downloadCount", 0),
            categories=[cat.get("name", "")
                        for cat in mod_data.get("categories", [])],
            authors=[author.get("name", "")
                     for author in mod_data.get("authors", [])],
            logo_url=mod_data.get("logo", {}).get("url"),
            last_updated=datetime.fromisoformat(
                mod_data["dateModified"].replace("Z", "+00:00"))
            if mod_data.get("dateModified") else None
        )

    def _parse_modpack_details(self, mod_data: Dict[str, Any]) -> ModpackDetails:
        """Parse detailed modpack data."""
        return ModpackDetails(
            id=mod_data["id"],
            name=mod_data["name"],
            summary=mod_data.get("summary", ""),
            description=mod_data.get("description", ""),
            download_count=mod_data.get("downloadCount", 0),
            categories=[cat.get("name", "")
                        for cat in mod_data.get("categories", [])],
            authors=[author.get("name", "")
                     for author in mod_data.get("authors", [])],
            logo_url=mod_data.get("logo", {}).get("url"),
            screenshots=[img.get("url", "")
                         for img in mod_data.get("screenshots", [])],
            last_updated=datetime.fromisoformat(
                mod_data["dateModified"].replace("Z", "+00:00"))
            if mod_data.get("dateModified") else None,
            game_version_latest=mod_data.get("latestFilesIndexes", [{}])[
                0].get("gameVersion"),
            mod_loader=mod_data.get("latestFilesIndexes", [{}])[
                0].get("modLoader")
        )

    def _parse_modpack_version(self, file_data: Dict[str, Any]) -> ModpackVersion:
        """Parse modpack version/file data."""
        return ModpackVersion(
            id=file_data["id"],
            display_name=file_data["displayName"],
            file_name=file_data["fileName"],
            file_date=datetime.fromisoformat(
                file_data["fileDate"].replace("Z", "+00:00")),
            download_url=file_data.get("downloadUrl", ""),
            game_versions=file_data.get("gameVersions", []),
            mod_loader=file_data.get("modLoader"),
            file_size=file_data.get("fileLength", 0)
        )

    async def search_modpacks(
        self,
        search_term: str = "",
        category_filter: Optional[str] = None,
        sort_field: str = "Popularity",
        sort_order: str = "desc",
        page_size: int = 20,
        index: int = 0
    ) -> List[ModpackSearchResult]:
        """
        Search for modpacks on CurseForge or return fallback suggestions.

        Args:
            search_term: Search query string
            category_filter: Filter by category name
            sort_field: Sort field (Popularity, Name, Author, TotalDownloads, etc.)
            sort_order: Sort order (asc, desc)
            page_size: Number of results per page (max 50)
            index: Starting index for pagination

        Returns:
            List of modpack search results

        Raises:
            ModpackServiceError: On API errors
        """
        # If no API key, return fallback suggestions
        if not self.is_api_available():
            logger.info(
                "No CurseForge API key available, returning fallback suggestions")
            fallback_results = await self.search_fallback_modpacks(search_term)

            # Convert fallback results to ModpackSearchResult format
            modpacks = []
            for i, pack in enumerate(fallback_results[:page_size]):
                modpack = ModpackSearchResult(
                    id=1000000 + i,  # Use fake IDs for fallback results
                    name=pack["name"],
                    summary=pack["description"],
                    download_count=0,  # Unknown for fallback
                    categories=[pack["difficulty"]],
                    authors=["Community"],
                    logo_url=None,
                    last_updated=None
                )
                modpacks.append(modpack)

            return modpacks

        # Use CurseForge API if available
        params = {
            "gameId": self.MINECRAFT_GAME_ID,
            "categoryId": self.MODPACK_CATEGORY_ID,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "pageSize": min(page_size, 50),
            "index": index
        }

        if search_term:
            params["searchFilter"] = search_term

        try:
            response = await self._make_request("/mods/search", params)

            modpacks = []
            for mod_data in response.get("data", []):
                try:
                    modpack = self._parse_modpack_search_result(mod_data)

                    # Apply category filter if specified
                    if category_filter and category_filter.lower() not in [cat.lower() for cat in modpack.categories]:
                        continue

                    modpacks.append(modpack)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse modpack {mod_data.get('id', 'unknown')}: {e}")
                    continue

            logger.info(
                f"Found {len(modpacks)} modpacks for search: '{search_term}'")
            return modpacks

        except Exception as e:
            logger.error(f"Failed to search modpacks: {e}")
            # If API fails, fall back to suggestions
            logger.info("API failed, falling back to suggestions")
            fallback_results = await self.search_fallback_modpacks(search_term)

            modpacks = []
            for i, pack in enumerate(fallback_results[:page_size]):
                modpack = ModpackSearchResult(
                    id=1000000 + i,
                    name=pack["name"],
                    summary=pack["description"],
                    download_count=0,
                    categories=[pack["difficulty"]],
                    authors=["Community"],
                    logo_url=None,
                    last_updated=None
                )
                modpacks.append(modpack)

            return modpacks

    async def get_modpack_details(self, modpack_id: int) -> ModpackDetails:
        """
        Get detailed information about a specific modpack.

        Args:
            modpack_id: CurseForge modpack ID

        Returns:
            Detailed modpack information

        Raises:
            ModpackNotFoundError: If modpack doesn't exist
            ModpackServiceError: On API errors
        """
        try:
            response = await self._make_request(f"/mods/{modpack_id}")

            mod_data = response.get("data")
            if not mod_data:
                raise ModpackNotFoundError(f"Modpack {modpack_id} not found")

            modpack = self._parse_modpack_details(mod_data)
            logger.info(
                f"Retrieved details for modpack: {modpack.name} (ID: {modpack_id})")

            return modpack

        except ModpackNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to get modpack details for ID {modpack_id}: {e}")
            raise ModpackServiceError(
                f"Failed to retrieve modpack details: {e}")

    async def get_modpack_versions(self, modpack_id: int, game_version: Optional[str] = None) -> List[ModpackVersion]:
        """
        Get available versions/files for a modpack.

        Args:
            modpack_id: CurseForge modpack ID
            game_version: Filter by Minecraft version (optional)

        Returns:
            List of available modpack versions

        Raises:
            ModpackNotFoundError: If modpack doesn't exist
            ModpackServiceError: On API errors
        """
        params = {}
        if game_version:
            params["gameVersion"] = game_version

        try:
            response = await self._make_request(f"/mods/{modpack_id}/files", params)

            files_data = response.get("data", [])
            if not files_data:
                logger.warning(f"No files found for modpack {modpack_id}")
                return []

            versions = []
            for file_data in files_data:
                try:
                    version = self._parse_modpack_version(file_data)
                    versions.append(version)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse file {file_data.get('id', 'unknown')}: {e}")
                    continue

            # Sort by file date (newest first)
            versions.sort(key=lambda v: v.file_date, reverse=True)

            logger.info(
                f"Found {len(versions)} versions for modpack {modpack_id}")
            return versions

        except Exception as e:
            logger.error(
                f"Failed to get modpack versions for ID {modpack_id}: {e}")
            raise ModpackServiceError(
                f"Failed to retrieve modpack versions: {e}")

    async def get_popular_modpacks(self, limit: int = 20) -> List[ModpackSearchResult]:
        """
        Get popular modpacks sorted by download count.

        Args:
            limit: Maximum number of modpacks to return

        Returns:
            List of popular modpacks
        """
        return await self.search_modpacks(
            sort_field="TotalDownloads",
            sort_order="desc",
            page_size=limit
        )

    async def get_recently_updated_modpacks(self, limit: int = 20) -> List[ModpackSearchResult]:
        """
        Get recently updated modpacks.

        Args:
            limit: Maximum number of modpacks to return

        Returns:
            List of recently updated modpacks
        """
        return await self.search_modpacks(
            sort_field="LastUpdated",
            sort_order="desc",
            page_size=limit
        )

    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
        logger.info("ModpackService cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values() if entry.is_expired())

        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries
        }

    async def validate_custom_modpack_url(self, url: str) -> Dict[str, Any]:
        """
        Validate a custom modpack URL and extract metadata.

        Args:
            url: Direct download URL to modpack file

        Returns:
            Dictionary with file metadata

        Raises:
            ModpackServiceError: If URL is invalid or inaccessible
        """
        if not self.client:
            raise ModpackServiceError(
                "Service not initialized. Use async context manager.")

        try:
            # Make a HEAD request to get file info without downloading
            response = await self.client.head(url, follow_redirects=True)

            if response.status_code >= 400:
                raise ModpackServiceError(
                    f"URL not accessible: HTTP {response.status_code}")

            # Extract file information from headers
            content_length = response.headers.get("content-length")
            content_type = response.headers.get("content-type", "")

            # Try to extract filename from URL or Content-Disposition header
            file_name = url.split("/")[-1]
            if "content-disposition" in response.headers:
                import re
                cd_header = response.headers["content-disposition"]
                filename_match = re.search(r'filename[*]?=([^;]+)', cd_header)
                if filename_match:
                    file_name = filename_match.group(1).strip('"\'')

            # Validate file type
            valid_extensions = ['.zip', '.jar', '.mrpack']
            if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
                logger.warning(f"File may not be a valid modpack: {file_name}")

            return {
                "file_name": file_name,
                "file_size": int(content_length) if content_length else 0,
                "content_type": content_type,
                "url": str(response.url),  # Final URL after redirects
                "accessible": True
            }

        except httpx.HTTPError as e:
            raise ModpackServiceError(f"Failed to validate URL: {str(e)}")

    async def create_custom_modpack(
        self,
        name: str,
        download_url: str,
        description: str = "",
        mod_loader: Optional[str] = None,
        game_version: Optional[str] = None
    ) -> CustomModpackSource:
        """
        Create a custom modpack source from a direct URL.

        Args:
            name: Display name for the modpack
            download_url: Direct download URL
            description: Optional description
            mod_loader: Mod loader type (Forge, Fabric, etc.)
            game_version: Minecraft version

        Returns:
            CustomModpackSource object

        Raises:
            ModpackServiceError: If URL validation fails
        """
        # Validate the URL first
        url_info = await self.validate_custom_modpack_url(download_url)

        return CustomModpackSource(
            name=name,
            description=description,
            download_url=url_info["url"],
            file_name=url_info["file_name"],
            mod_loader=mod_loader,
            game_version=game_version,
            source_type="url"
        )

    async def get_popular_modpack_sites(self) -> List[Dict[str, str]]:
        """
        Get a list of popular modpack hosting sites for user reference.

        Returns:
            List of site information
        """
        return [
            {
                "name": "CurseForge",
                "url": "https://www.curseforge.com/minecraft/modpacks",
                "description": "Official CurseForge modpack repository",
                "api_required": True,
                "instructions": "Browse modpacks and copy the download link from the Files tab"
            },
            {
                "name": "Modrinth",
                "url": "https://modrinth.com/modpacks",
                "description": "Modern modpack platform with direct downloads",
                "api_required": False,
                "instructions": "Click on a modpack version and copy the download link"
            },
            {
                "name": "ATLauncher",
                "url": "https://atlauncher.com/packs",
                "description": "ATLauncher modpack repository",
                "api_required": False,
                "instructions": "Find the modpack and look for direct download links"
            },
            {
                "name": "Technic Platform",
                "url": "https://www.technicpack.net/modpacks",
                "description": "Technic modpack platform",
                "api_required": False,
                "instructions": "Browse modpacks and find download links in modpack details"
            },
            {
                "name": "Feed The Beast",
                "url": "https://www.feed-the-beast.com/modpacks",
                "description": "FTB official modpacks",
                "api_required": False,
                "instructions": "Download modpack files directly from FTB website"
            }
        ]

    async def search_fallback_modpacks(self, search_term: str = "") -> List[Dict[str, Any]]:
        """
        Fallback search when CurseForge API is not available.
        Returns popular modpack suggestions with instructions.

        Args:
            search_term: Search query (used for filtering suggestions)

        Returns:
            List of modpack suggestions with setup instructions
        """
        popular_modpacks = [
            {
                "name": "All The Mods 9",
                "description": "Kitchen sink modpack with tons of mods",
                "game_version": "1.20.1",
                "mod_loader": "Forge",
                "instructions": "Visit CurseForge or ATLauncher to download",
                "estimated_size": "~500MB",
                "difficulty": "Advanced"
            },
            {
                "name": "FTB Skies",
                "description": "Skyblock-style modpack with quests",
                "game_version": "1.19.2",
                "mod_loader": "Forge",
                "instructions": "Available on FTB App or CurseForge",
                "estimated_size": "~300MB",
                "difficulty": "Intermediate"
            },
            {
                "name": "Better Minecraft",
                "description": "Enhanced vanilla experience with performance mods",
                "game_version": "1.20.1",
                "mod_loader": "Fabric",
                "instructions": "Download from CurseForge or Modrinth",
                "estimated_size": "~200MB",
                "difficulty": "Beginner"
            },
            {
                "name": "Create: Above and Beyond",
                "description": "Tech modpack focused on Create mod",
                "game_version": "1.16.5",
                "mod_loader": "Forge",
                "instructions": "Available on CurseForge",
                "estimated_size": "~400MB",
                "difficulty": "Intermediate"
            },
            {
                "name": "Enigmatica 6",
                "description": "Expert-style kitchen sink modpack",
                "game_version": "1.16.5",
                "mod_loader": "Forge",
                "instructions": "Download from CurseForge",
                "estimated_size": "~600MB",
                "difficulty": "Expert"
            }
        ]

        # Filter by search term if provided
        if search_term:
            search_lower = search_term.lower()
            popular_modpacks = [
                pack for pack in popular_modpacks
                if search_lower in pack["name"].lower() or search_lower in pack["description"].lower()
            ]

        return popular_modpacks

    def is_api_available(self) -> bool:
        """Check if CurseForge API is available (has API key)."""
        return self.api_key is not None


# Convenience function for creating service instances
async def create_modpack_service(api_key: Optional[str] = None) -> ModpackService:
    """
    Create and initialize a ModpackService instance.

    Args:
        api_key: Optional CurseForge API key

    Returns:
        Initialized ModpackService instance
    """
    service = ModpackService(api_key=api_key)
    await service.__aenter__()
    return service
