/**
 * 电能监测（Page3）- 与 xtck_deploy API 对应
 * ckqy/ljydtj, gfqy/ljfdtj, cdzqy/ljydtj, ydfdtj/chart, yjtj, zjyj, cnsy
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { DataCard } from "@/components/carbon/data-view"
import { StatTypeSelect, type StatType } from "@/components/carbon/stat-type"

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon/page3")({
  component: Page3Energy,
})

function Page3Energy() {
  const [statType, setStatType] = useState<StatType>("day")

  const ckqyQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "ckqy", "ljydtj"],
    queryFn: async () => {
      const res = await fetch("/api/page3/ckqy/ljydtj")
      return res.json()
    },
  })
  const gfqyQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "gfqy", "ljfdtj"],
    queryFn: async () => {
      const res = await fetch("/api/page3/gfqy/ljfdtj")
      return res.json()
    },
  })
  const cdzqyQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "cdzqy", "ljydtj"],
    queryFn: async () => {
      const res = await fetch("/api/page3/cdzqy/ljydtj")
      return res.json()
    },
  })
  const chartQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "ydfdtj", "chart", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page3/ydfdtj/chart/${statType}`)
      return res.json()
    },
  })
  const yjtjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "yjtj", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page3/yjtj/${statType}`)
      return res.json()
    },
  })
  const zjyjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "zjyj"],
    queryFn: async () => {
      const res = await fetch("/api/page3/zjyj")
      return res.json()
    },
  })
  const cnsyQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page3", "cnsy"],
    queryFn: async () => {
      const res = await fetch("/api/page3/cnsy")
      return res.json()
    },
  })

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader
        eyebrow="电能监测"
        title="Page3 电能监测"
        description="仓库用电、光伏发电、充电桩用电、用电发电图表、用能统计、重点预警、储能收益"
      />
      <PageSection>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">统计粒度</div>
          <StatTypeSelect value={statType} onChange={setStatType} />
        </div>
        {(ckqyQuery.isLoading ||
          gfqyQuery.isLoading ||
          cdzqyQuery.isLoading ||
          chartQuery.isLoading ||
          yjtjQuery.isLoading ||
          zjyjQuery.isLoading ||
          cnsyQuery.isLoading) && <div className="text-sm text-muted-foreground">正在加载数据…</div>}
        {(ckqyQuery.isError ||
          gfqyQuery.isError ||
          cdzqyQuery.isError ||
          chartQuery.isError ||
          yjtjQuery.isError ||
          zjyjQuery.isError ||
          cnsyQuery.isError) && <div className="text-sm text-destructive">部分数据加载失败，请检查后端接口或网络。</div>}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <DataCard title="仓库企业累计用电 ljydtj" data={ckqyQuery.data?.data ?? {}} />
          <DataCard title="光伏企业累计发电 ljfdtj" data={gfqyQuery.data?.data ?? {}} />
          <DataCard title="充电桩企业累计用电" data={cdzqyQuery.data?.data ?? {}} />
          <DataCard
            title={`用电发电统计图 ydfdtj/chart（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={chartQuery.data?.data ?? {}}
          />
          <DataCard
            title={`用能统计 yjtj（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={yjtjQuery.data?.data ?? {}}
          />
          <DataCard title="重点预警 zjyj" data={zjyjQuery.data?.data ?? {}} />
          <div className="md:col-span-2">
            <DataCard title="储能收益 cnsy" data={cnsyQuery.data?.data ?? {}} />
          </div>
        </div>
      </PageSection>
    </PageContainer>
  )
}
