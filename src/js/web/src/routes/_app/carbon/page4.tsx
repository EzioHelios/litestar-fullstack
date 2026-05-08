/**
 * 碳能协同（Page4）- 与 xtck_deploy API 对应
 * tpfltj, tpflzl, tpfl/ckqypx, tpfl/year, tpfltj/chart, yjtj, qytpfyj, cktpfqd/chart, zjyj
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { DataCard } from "@/components/carbon/data-view"
import { StatTypeSelect, type StatType } from "@/components/carbon/stat-type"

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon/page4")({
  component: Page4CarbonEnergy,
})

function Page4CarbonEnergy() {
  const [statType, setStatType] = useState<StatType>("day")

  const tpfltjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "tpfltj"],
    queryFn: async () => {
      const res = await fetch("/api/page4/tpfltj")
      return res.json()
    },
  })
  const tpflzlQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "tpflzl", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page4/tpflzl/${statType}`)
      return res.json()
    },
  })
  const ckqypxQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "tpfl", "ckqypx", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page4/tpfl/ckqypx/${statType}`)
      return res.json()
    },
  })
  const yearQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "tpfl", "year"],
    queryFn: async () => {
      const res = await fetch("/api/page4/tpfl/year")
      return res.json()
    },
  })
  const chartQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "tpfltj", "chart", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page4/tpfltj/chart/${statType}`)
      return res.json()
    },
  })
  const yjtjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "yjtj", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page4/yjtj/${statType}`)
      return res.json()
    },
  })
  const qytpfyjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "qytpfyj", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page4/qytpfyj/${statType}`)
      return res.json()
    },
  })
  const cktpfqdQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "cktpfqd", "chart", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page4/cktpfqd/chart/${statType}`)
      return res.json()
    },
  })
  const zjyjQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page4", "zjyj"],
    queryFn: async () => {
      const res = await fetch("/api/page4/zjyj")
      return res.json()
    },
  })

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader
        eyebrow="碳能协同"
        title="Page4 碳能协同"
        description="碳排分类统计、碳排分类总量、仓库企业排行、年度分类、图表、用能统计、企业碳排预警、仓库碳排强度、重点预警"
      />
      <PageSection>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">统计粒度</div>
          <StatTypeSelect value={statType} onChange={setStatType} />
        </div>
        {(tpfltjQuery.isLoading ||
          tpflzlQuery.isLoading ||
          ckqypxQuery.isLoading ||
          yearQuery.isLoading ||
          chartQuery.isLoading ||
          yjtjQuery.isLoading ||
          qytpfyjQuery.isLoading ||
          cktpfqdQuery.isLoading ||
          zjyjQuery.isLoading) && <div className="text-sm text-muted-foreground">正在加载数据…</div>}
        {(tpfltjQuery.isError ||
          tpflzlQuery.isError ||
          ckqypxQuery.isError ||
          yearQuery.isError ||
          chartQuery.isError ||
          yjtjQuery.isError ||
          qytpfyjQuery.isError ||
          cktpfqdQuery.isError ||
          zjyjQuery.isError) && <div className="text-sm text-destructive">部分数据加载失败，请检查后端接口或网络。</div>}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <DataCard title="碳排分类统计 tpfltj" data={tpfltjQuery.data?.data ?? {}} />
          <DataCard
            title={`碳排分类总量 tpflzl（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={tpflzlQuery.data?.data ?? {}}
          />
          <DataCard
            title={`仓库企业排行 tpfl/ckqypx（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={ckqypxQuery.data?.data ?? {}}
          />
          <DataCard title="年度分类 tpfl/year" data={yearQuery.data?.data ?? {}} />
          <DataCard
            title={`碳排分类统计图 tpfltj/chart（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={chartQuery.data?.data ?? {}}
          />
          <DataCard
            title={`用能统计 yjtj（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={yjtjQuery.data?.data ?? {}}
          />
          <DataCard
            title={`企业碳排预警 qytpfyj（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={qytpfyjQuery.data?.data ?? {}}
          />
          <DataCard
            title={`仓库碳排强度 cktpfqd/chart（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
            data={cktpfqdQuery.data?.data ?? {}}
          />
          <DataCard title="重点预警 zjyj" data={zjyjQuery.data?.data ?? {}} />
        </div>
      </PageSection>
    </PageContainer>
  )
}
