"""
Test file for ModpackService to verify CurseForge API integration.
"""

import asyncio
from services.modpack_service import (
    ModpackService,
    ModpackServiceError,
    APIConnectionError,
    ModpackNotFoundError
)


async def test_modpack_service_basic():
    """Test basic ModpackService functionality."""
    async with ModpackService() as service:
        # Test search functionality
        print("Testing modpack search...")
        results = await service.search_modpacks("FTB", page_size=5)

        assert len(results) > 0, "Should find some modpacks"
        print(f"Found {len(results)} modpacks")

        for modpack in results[:2]:
            print(
                f"- {modpack.name} (ID: {modpack.id}) - {modpack.download_count} downloads")

        # Test modpack details
        if results:
            first_modpack = results[0]
            print(f"\nTesting modpack details for: {first_modpack.name}")

            details = await service.get_modpack_details(first_modpack.id)
            assert details.id == first_modpack.id
            assert details.name == first_modpack.name
            print(f"Details: {details.summary}")

            # Test modpack versions
            print(f"\nTesting modpack versions for: {first_modpack.name}")
            versions = await service.get_modpack_versions(first_modpack.id)

            if versions:
                print(f"Found {len(versions)} versions")
                latest_version = versions[0]
                print(
                    f"Latest: {latest_version.display_name} ({latest_version.file_date})")
            else:
                print("No versions found")


async def test_popular_modpacks():
    """Test popular modpacks retrieval."""
    async with ModpackService() as service:
        print("\nTesting popular modpacks...")
        popular = await service.get_popular_modpacks(limit=5)

        assert len(popular) > 0, "Should find popular modpacks"
        print(f"Found {len(popular)} popular modpacks")

        for modpack in popular:
            print(f"- {modpack.name}: {modpack.download_count:,} downloads")


async def test_error_handling():
    """Test error handling for invalid requests."""
    async with ModpackService() as service:
        print("\nTesting error handling...")

        # Test invalid modpack ID
        try:
            await service.get_modpack_details(999999999)
            assert False, "Should have raised ModpackNotFoundError"
        except ModpackNotFoundError:
            print("✓ Correctly handled invalid modpack ID")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")


async def test_caching():
    """Test response caching functionality."""
    async with ModpackService() as service:
        print("\nTesting caching...")

        # First request
        start_time = asyncio.get_event_loop().time()
        results1 = await service.search_modpacks("FTB", page_size=3)
        first_request_time = asyncio.get_event_loop().time() - start_time

        # Second request (should be cached)
        start_time = asyncio.get_event_loop().time()
        results2 = await service.search_modpacks("FTB", page_size=3)
        second_request_time = asyncio.get_event_loop().time() - start_time

        assert len(results1) == len(results2), "Cached results should match"
        assert second_request_time < first_request_time, "Cached request should be faster"

        print(f"First request: {first_request_time:.3f}s")
        print(f"Cached request: {second_request_time:.3f}s")

        # Check cache stats
        stats = service.get_cache_stats()
        print(f"Cache stats: {stats}")
        assert stats["active_entries"] > 0, "Should have cached entries"


async def main():
    """Run all tests."""
    print("=== ModpackService Test Suite ===\n")

    try:
        await test_modpack_service_basic()
        await test_popular_modpacks()
        await test_error_handling()
        await test_caching()

        print("\n=== All tests passed! ===")

    except Exception as e:
        print(f"\n=== Test failed: {e} ===")
        raise


if __name__ == "__main__":
    asyncio.run(main())
