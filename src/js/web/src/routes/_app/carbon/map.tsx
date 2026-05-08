/**
 * 地图页 - 与 xtck_deploy API 对应：popup, monitorSector/list, vedio/popup, videos
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { DataCard } from "@/components/carbon/data-view"

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon/map")({
  component: MapPage,
})

function MapPage() {
  const sectorsQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "map", "monitorSector", "list"],
    queryFn: async () => {
      const res = await fetch("/api/map/monitorSector/list")
      return res.json()
    },
  })
  const videosQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "map", "videos"],
    queryFn: async () => {
      const res = await fetch("/api/map/videos")
      return res.json()
    },
  })

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader
        eyebrow="地图"
        title="监测地图"
        description="监测区域列表、视频点位；popup 接口需 area_id/vid 由地图点击触发"
      />
      <PageSection>
        {(sectorsQuery.isLoading || videosQuery.isLoading) && <div className="text-sm text-muted-foreground">正在加载数据…</div>}
        {(sectorsQuery.isError || videosQuery.isError) && <div className="text-sm text-destructive">部分数据加载失败，请检查后端接口或网络。</div>}
        <div className="grid gap-6 md:grid-cols-2">
          <DataCard title="监测区域 monitorSector/list" data={sectorsQuery.data?.data ?? []} />
          <DataCard title="视频点位 map/videos" data={videosQuery.data?.data ?? []} />
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          区域弹窗: GET /api/map/popup/&#123;area_id&#125; ；视频弹窗: GET /api/map/vedio/popup/&#123;vid&#125;
        </p>
      </PageSection>
    </PageContainer>
  )
}
