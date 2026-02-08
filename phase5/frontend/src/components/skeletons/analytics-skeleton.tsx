import { Skeleton } from "@/components/ui/skeleton";

export function ChartSkeleton() {
  return (
    <div className="p-6 border rounded-lg space-y-4">
      <Skeleton className="h-5 w-32" />
      <div className="h-[200px] flex items-end justify-around gap-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton
            key={i}
            className="w-8"
            style={{ height: `${Math.random() * 60 + 40}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export function DonutChartSkeleton() {
  return (
    <div className="p-6 border rounded-lg space-y-4">
      <Skeleton className="h-5 w-32" />
      <div className="flex items-center justify-center">
        <Skeleton className="h-40 w-40 rounded-full" />
      </div>
      <div className="flex justify-center gap-4">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-20" />
      </div>
    </div>
  );
}

export function AnalyticsSkeleton() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-96" />
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="p-4 border rounded-lg space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-16" />
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <DonutChartSkeleton />
        <ChartSkeleton />
      </div>

      {/* Additional Stats */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="p-6 border rounded-lg space-y-4">
          <Skeleton className="h-5 w-32" />
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-8" />
              </div>
            ))}
          </div>
        </div>
        <div className="p-6 border rounded-lg space-y-4">
          <Skeleton className="h-5 w-32" />
          <div className="flex items-center justify-center">
            <Skeleton className="h-24 w-24 rounded-full" />
          </div>
          <Skeleton className="h-4 w-full" />
        </div>
        <div className="p-6 border rounded-lg space-y-4">
          <Skeleton className="h-5 w-32" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-3 bg-muted/50 rounded-lg">
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
