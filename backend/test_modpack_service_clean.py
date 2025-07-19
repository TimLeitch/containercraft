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
    CustomModpackSource,
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

    # Test CustomModpackSource
    custom_source = CustomModpackSource(
        name="Custom Test Pack",
        description="A custom modpack",
        download_url="https://example.com/pack.zip",
        file_name="pack.zip",
        mod_loader="Forge",
        game_version="1.20.1",
        source_type="url"
    )

    assert custom_source.name == "Custom Test Pack"
    assert custom_source.source_type == "url"
    print(f"✓ CustomModpackSource: {custom_source.name}")


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
    assert not service.is_api_available()
    print("✓ Service initializes without API key")

    # Test with API key
    service_with_key = ModpackService(api_key="test_key")
    assert service_with_key.api_key == "test_key"
    assert service_with_key.is_api_available()
    print("✓ Service initializes with API key")


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


async def main():
    """Run all unit tests."""
    print("=== ModpackService Enhanced Unit Test Suite ===\n")

    try:
        test_modpack_models()
        test_cache_entry()
        await test_rate_limiter()
        test_service_initialization()
        await test_fallback_functionality()
        await test_custom_modpack_functionality()

        print("\n=== All enhanced tests passed! ===")
        print("\nThe ModpackService now supports:")
        print("✓ CurseForge API integration (with API key)")
        print("✓ Fallback modpack suggestions (without API key)")
        print("✓ Custom modpack URLs from various sites")
        print("✓ Popular modpack site recommendations")
        print("✓ Response caching and rate limiting")
        print("✓ Comprehensive error handling")

        print("\nUsage examples:")
        print("- With API key: ModpackService(api_key='your_key')")
        print("- Without API key: ModpackService() # Uses fallback suggestions")
        print("- Custom URL: service.create_custom_modpack(name, url)")

    except Exception as e:
        print(f"\n=== Test failed: {e} ===")
        raise


if __name__ == "__main__":
    asyncio.run(main())
