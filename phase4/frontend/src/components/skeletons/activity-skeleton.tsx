import { Skeleton } from "@/components/ui/skeleton";

export function ActivityItemSkeleton() {
  return (
    <div className="flex items-start gap-3 p-3">
      <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-1">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/4" />
      </div>
    </div>
  );
}

export function ActivityFeedSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-1 divide-y">
      {Array.from({ length: count }).map((_, i) => (
        <ActivityItemSkeleton key={i} />
      ))}
    </div>
  );
}
