"""
Unit tests for ModpackService to verify implementation without API calls.
"""

import asyncio
from datetime import datetime
from services.modpack_service import (
    ModpackService,
    ModpackSearchResult,
    ModpackDetails,
    ModpackVersion,
    CacheEntry,
    RateLimiter
)


def test_modpack_models():
    """Test Pydantic models for modpack data."""
    print("Testing Pydantic models...")

    # Test ModpackSearchResult
    search_result = ModpackSearchResult(
        id=123456,
        name="Test Modpack",
        summary="A test modpack for unit testing",
        download_count=50000,
        categories=["Technology", "Adventure"],
        authors=["TestAuthor"],
        logo_url="https://example.com/logo.png"
    )

    assert search_result.id == 123456
    assert search_result.name == "Test Modpack"
    assert len(search_result.categories) == 2
    print(f"✓ ModpackSearchResult: {search_result.name}")

    # Test ModpackDetails
    details = ModpackDetails(
        id=123456,
        name="Test Modpack",
        summary="A test modpack",
        description="Detailed description of the test modpack",
        download_count=50000,
        categories=["Technology"],
        authors=["TestAuthor"],
        screenshots=["https://example.com/screenshot1.png"]
    )

    assert details.id == 123456
    assert len(details.screenshots) == 1
    print(f"✓ ModpackDetails: {details.name}")

    # Test ModpackVersion
    version = ModpackVersion(
        id=789012,
        display_name="Test Modpack v1.0.0",
        file_name="test-modpack-1.0.0.zip",
        file_date=datetime.now(),
        download_url="https://example.com/download",
        game_versions=["1.19.2", "1.20.1"],
        mod_loader="Forge",
        file_size=1024000
    )

    assert version.id == 789012
    assert len(version.game_versions) == 2
    assert version.mod_loader == "Forge"
    print(f"✓ ModpackVersion: {version.display_name}")


def test_cache_entry():
    """Test cache entry functionality."""
    print("\nTesting cache entry...")

    # Test non-expired entry
    entry = CacheEntry("test_data", ttl_seconds=60)
    assert not entry.is_expired()
    assert entry.data == "test_data"
    print("✓ Cache entry created and not expired")

    # Test expired entry
    expired_entry = CacheEntry("old_data", ttl_seconds=0)
    import time
    time.sleep(0.1)  # Wait a bit to ensure expiration
    assert expired_entry.is_expired()
    print("✓ Cache entry correctly expires")


async def test_rate_limiter():
    """Test rate limiter functionality."""
    print("\nTesting rate limiter...")

    # Test rate limiter with high limit (should not block)
    limiter = RateLimiter(max_requests=10, window_seconds=1)

    start_time = asyncio.get_event_loop().time()
    await limiter.acquire()
    await limiter.acquire()
    end_time = asyncio.get_event_loop().time()

    # Should be very fast since we're under the limit
    assert (end_time - start_time) < 0.1
    print("✓ Rate limiter allows requests under limit")

    # Test rate limiter behavior
    assert len(limiter.requests) == 2
    print("✓ Rate limiter tracks requests")


def test_service_initialization():
    """Test ModpackService initialization."""
    print("\nTesting service initialization...")

    # Test without API key
    service = ModpackService()
    assert service.api_key is None
    assert service.cache == {}
    assert service.rate_limiter is not None
    print("✓ Service initializes without API key")

    # Test with API key
    service_with_key = ModpackService(api_key="test_key")
    assert service_with_key.api_key == "test_key"
    print("✓ Service initializes with API key")


def test_cache_operations():
    """Test cache operations."""
    print("\nTesting cache operations...")

    service = ModpackService()

    # Test cache key generation
    cache_key = service._get_cache_key(
        "/test", {"param1": "value1", "param2": "value2"})
    expected_key = "/test?param1=value1&param2=value2"
    assert cache_key == expected_key
    print("✓ Cache key generation works correctly")

    # Test caching data
    test_data = {"test": "data"}
    service._cache_data(cache_key, test_data, ttl_seconds=60)

    # Test retrieving cached data
    cached_data = service._get_cached_data(cache_key)
    assert cached_data == test_data
    print("✓ Data caching and retrieval works")

    # Test cache stats
    stats = service.get_cache_stats()
    assert stats["total_entries"] == 1
    assert stats["active_entries"] == 1
    assert stats["expired_entries"] == 0
    print("✓ Cache statistics work correctly")

    # Test cache clearing
    service.clear_cache()
    assert len(service.cache) == 0
    print("✓ Cache clearing works")


def test_data_parsing():
    """Test data parsing methods."""
    print("\nTesting data parsing...")

    service = ModpackService()

    # Mock CurseForge API response data
    mock_search_data = {
        "id": 123456,
        "name": "Test Modpack",
        "summary": "A test modpack",
        "downloadCount": 50000,
        "categories": [{"name": "Technology"}, {"name": "Adventure"}],
        "authors": [{"name": "TestAuthor"}],
        "logo": {"url": "https://example.com/logo.png"},
        "dateModified": "2024-01-15T10:30:00Z"
    }

    # Test search result parsing
    search_result = service._parse_modpack_search_result(mock_search_data)
    assert search_result.id == 123456
    assert search_result.name == "Test Modpack"
    assert len(search_result.categories) == 2
    assert search_result.categories[0] == "Technology"
    print("✓ Search result parsing works")

    # Test details parsing
    mock_details_data = {
        **mock_search_data,
        "description": "Detailed description",
        "screenshots": [{"url": "https://example.com/screenshot1.png"}],
        "latestFilesIndexes": [{"gameVersion": "1.19.2", "modLoader": "Forge"}]
    }

    details = service._parse_modpack_details(mock_details_data)
    assert details.description == "Detailed description"
    assert len(details.screenshots) == 1
    assert details.game_version_latest == "1.19.2"
    print("✓ Details parsing works")

    # Test version parsing
    mock_version_data = {
        "id": 789012,
        "displayName": "Test Modpack v1.0.0",
        "fileName": "test-modpack-1.0.0.zip",
        "fileDate": "2024-01-15T10:30:00Z",
        "downloadUrl": "https://example.com/download",
        "gameVersions": ["1.19.2", "1.20.1"],
        "modLoader": "Forge",
        "fileLength": 1024000
    }

    version = service._parse_modpack_version(mock_version_data)
    assert version.id == 789012
    assert version.display_name == "Test Modpack v1.0.0"
    assert len(version.game_versions) == 2
    assert version.file_size == 1024000
    print("✓ Version parsing works")


async def test_fallback_functionality():
    """Test fallback functionality when API is not available."""
    print("\nTesting fallback functionality...")

    # Test service without API key
    service = ModpackService()
    assert not service.is_api_available()
    print("✓ Service correctly detects no API key")

    # Test fallback search
    async with service:
        fallback_results = await service.search_fallback_modpacks("FTB")
        assert len(fallback_results) > 0

        # Check that results contain expected fields
        first_result = fallback_results[0]
        assert "name" in first_result
        assert "description" in first_result
        assert "instructions" in first_result
        print(f"✓ Fallback search returned {len(fallback_results)} results")

        # Test search_modpacks fallback
        search_results = await service.search_modpacks("Better", page_size=3)
        assert len(search_results) > 0
        assert all(isinstance(result, ModpackSearchResult)
                   for result in search_results)
        print(
            f"✓ search_modpacks fallback returned {len(search_results)} results")


async def test_custom_modpack_functionality():
    """Test custom modpack URL functionality."""
    print("\nTesting custom modpack functionality...")

    service = ModpackService()

    # Test popular sites list
    sites = await service.get_popular_modpack_sites()
    assert len(sites) > 0

    # Check that each site has required fields
    for site in sites:
        assert "name" in site
        assert "url" in site
        assert "description" in site
        assert "instructions" in site

    print(f"✓ Retrieved {len(sites)} popular modpack sites")

    # Test custom modpack source creation (without actual URL validation)
    from services.modpack_service import CustomModpackSource
    custom_source = CustomModpackSource(
        name="Test Custom Modpack",
        description="A test custom modpack",
        download_url="https://example.com/modpack.zip",
        file_name="modpack.zip",
        mod_loader="Forge",
        game_version="1.20.1",
        source_type="url"
    )

    assert custom_source.name == "Test Custom Modpack"
    assert custom_source.source_type == "url"
    print("✓ Custom modpack source creation works")


async def main():
    """Run all unit tests."""
    print("=== ModpackService Unit Test Suite ===\n")

    try:
        test_modpack_models()
        test_cache_entry()
        await test_rate_limiter()
        test_service_initialization()
        test_cache_operations()
        test_data_parsing()
        await test_fallback_functionality()
        await test_custom_modpack_functionality()

        print("\n=== All unit tests passed! ===")
        print("\nNote: These tests verify the service structure and logic.")
        print("To test actual API integration, you'll need a CurseForge API key.")
        print(
            "Set the API key when creating the service: ModpackService(api_key='your_key')")
        print("\nThe service now supports:")
        print("- CurseForge API integration (with API key)")
        print("- Fallback modpack suggestions (without API key)")
        print("- Custom modpack URLs from various sites")
        print("- Popular modpack site recommendations")

    except Exception as e:
        print(f"\n=== Unit test failed: {e} ===")
        raise


if __name__ == "__main__":
    asyncio.run(main())


async def test_fallback_functionality():
    """Test fallback functionality when API is not available."""
    print("\nTesting fallback functionality...")

    # Test service without API key
    service = ModpackService()
    assert not service.is_api_available()
    print("✓ Service correctly detects no API key")

    # Test fallback search
    async with service:
        fallback_results = await service.search_fallback_modpacks("FTB")
        assert len(fallback_results) > 0

        # Check that results contain expected fields
        first_result = fallback_results[0]
        assert "name" in first_result
        assert "description" in first_result
        assert "instructions" in first_result
        print(f"✓ Fallback search returned {len(fallback_results)} results")

        # Test search_modpacks fallback
        search_results = await service.search_modpacks("Better", page_size=3)
        assert len(search_results) > 0
        assert all(isinstance(result, ModpackSearchResult)
                   for result in search_results)
        print(
            f"✓ search_modpacks fallback returned {len(search_results)} results")


async def test_custom_modpack_functionality():
    """Test custom modpack URL functionality."""
    print("\nTesting custom modpack functionality...")

    service = ModpackService()

    # Test popular sites list
    sites = await service.get_popular_modpack_sites()
    assert len(sites) > 0

    # Check that each site has required fields
    for site in sites:
        assert "name" in site
        assert "url" in site
        assert "description" in site
        assert "instructions" in site

    print(f"✓ Retrieved {len(sites)} popular modpack sites")

    # Test custom modpack source creation (without actual URL validation)
    from services.modpack_service import CustomModpackSource
    custom_source = CustomModpackSource(
        name="Test Custom Modpack",
        description="A test custom modpack",
        download_url="https://example.com/modpack.zip",
        file_name="modpack.zip",
        mod_loader="Forge",
        game_version="1.20.1",
        source_type="url"
    )

    assert custom_source.name == "Test Custom Modpack"
    assert custom_source.source_type == "url"
    print("✓ Custom modpack source creation works")
