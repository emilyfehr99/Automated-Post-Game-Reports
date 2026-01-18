import useSWR from 'swr';

// Default fetcher function
const fetcher = async (url) => {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Failed to fetch data');
    }
    return response.json();
};

/**
 * Custom SWR hook with optimized caching configuration
 * @param {string} key - The URL or key to fetch
 * @param {object} options - Additional SWR options
 * @returns {object} - { data, error, isLoading, isValidating }
 */
export function useSWRFetch(key, options = {}) {
    const { data, error, isValidating } = useSWR(key, fetcher, {
        // Don't revalidate on window focus (prevents unnecessary refetches)
        revalidateOnFocus: false,
        // Don't revalidate on reconnect (we'll let cache handle it)
        revalidateOnReconnect: false,
        // Dedupe requests within 5 minutes (300,000 ms)
        dedupingInterval: 300000,
        // Keep data in cache even when component unmounts
        keepPreviousData: true,
        // Retry on error
        shouldRetryOnError: true,
        errorRetryCount: 3,
        // Override with any custom options
        ...options,
    });

    return {
        data,
        error,
        isLoading: !error && !data,
        isValidating,
    };
}
