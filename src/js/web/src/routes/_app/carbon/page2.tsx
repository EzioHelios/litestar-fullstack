/**
 * 视频监控（Page2）- 与 xtck_deploy API 对应：yjzl, spgl, spjk, zjyj
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { DataCard } from "@/components/carbon/data-view"
import { StatTypeSelect, type StatType } from "@/components/carbon/stat-type"

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon/page2")({
  component: Page2Video,
})

function Page2Video() {
  const [statType, setStatType] = useState<StatType>("day")

  const yjzlQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page2", "yjzl", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page2/yjzl/${statType}`)
      return res.json()
    },
  })
  const spglQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page2", "spgl"],
    queryFn: async () => {
      const res = await fetch("/api/page2/spgl")
      return res.json()
    },
  })
  const spjkQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page2", "spjk"],
    queryFn: async () => {
      const res = await fetch("/api/page2/spjk")
      return res.json()
    },
  })
  const zjyjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page2", "zjyj"],
    queryFn: async () => {
      const res = await fetch("/api/page2/zjyj")
      return res.json()
    },
  })

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader
        eyebrow="视频监控"
        title="Page2 视频监控"
        description="预警质量、视频管理、视频监控、重点预警（与 xtck_deploy API 一致）"
      />
      <PageSection>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">统计粒度</div>
          <StatTypeSelect value={statType} onChange={setStatType} />
        </div>
        {(yjzlQuery.isLoading || spglQuery.isLoading || spjkQuery.isLoading || zjyjQuery.isLoading) && (
          <div className="text-sm text-muted-foreground">正在加载数据…</div>
        )}
        {(yjzlQuery.isError || spglQuery.isError || spjkQuery.isError || zjyjQuery.isError) && (
          <div className="text-sm text-destructive">部分数据加载失败，请检查后端接口或网络。</div>
        )}
        <div className="grid gap-6 md:grid-cols-2">
          <DataCard
            title={`预警质量 yjzl（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={yjzlQuery.data?.data ?? {}}
          />
          <DataCard title="视频管理 spgl" data={spglQuery.data?.data ?? {}} />
          <DataCard title="视频监控 spjk" data={spjkQuery.data?.data ?? {}} />
          <DataCard title="重点预警 zjyj" data={zjyjQuery.data?.data ?? {}} />
        </div>
      </PageSection>
    </PageContainer>
  )
}
