"use client";

/**
 * React Query Provider Component
 *
 * Wraps the application with QueryClientProvider to enable React Query
 * features throughout the app:
 * - Data fetching and caching
 * - Automatic refetching
 * - Optimistic updates
 * - Loading and error states
 */

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

export default function QueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  // Create QueryClient instance - useState ensures it's created only once
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Data is considered fresh for 1 minute
            staleTime: 60 * 1000,
            // Retry failed requests once
            retry: 1,
            // Refetch on window focus
            refetchOnWindowFocus: true,
            // Refetch on network reconnect
            refetchOnReconnect: true,
          },
          mutations: {
            // Don't retry mutations to avoid duplicate operations
            retry: 0,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Dev tools - only visible in development */}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
