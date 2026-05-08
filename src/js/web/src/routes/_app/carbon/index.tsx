/**
 * 态势总览（Page1）- 与 xtck_deploy dataapp API 一比一对应
 * API: ckxxgk, jcdwzxtj, ydfdzl, ydfdzl/qypx, tpfgl, yjzl, zjyj
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DataCard } from "@/components/carbon/data-view"
import { StatTypeSelect, type StatType } from "@/components/carbon/stat-type"
import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

type MonitorStats = {
  ydzs: number
  ydzx: number
  ydgz: number
  fdzs: number
  fdzx: number
  fdgz: number
  spzs: number
  spzx: number
  spgz: number
}

type ApiResponse<T> = {
  code: number
  msg: string
  data: T
}

export const Route = createFileRoute("/_app/carbon/")({
  component: Page1Overview,
})

function Page1Overview() {
  const [statType, setStatType] = useState<StatType>("day")

  const { data: ckInfo } = useQuery<ApiResponse<Record<string, unknown>>>({
    queryKey: ["carbon", "ckxxgk"],
    queryFn: async () => {
      const res = await fetch("/api/page1/ckxxgk")
      return res.json()
    },
  })

  const { data: stats } = useQuery<ApiResponse<MonitorStats>>({
    queryKey: ["carbon", "jcdwzxtj"],
    queryFn: async () => {
      const res = await fetch("/api/page1/jcdwzxtj")
      return res.json()
    },
  })

  const { data: ydfdzl } = useQuery<ApiResponse<Record<string, unknown>>>({
    queryKey: ["carbon", "ydfdzl", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page1/ydfdzl/${statType}`)
      return res.json()
    },
  })

  const { data: ydfdzlRank } = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "ydfdzl", "qypx", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page1/ydfdzl/qypx/${statType}`)
      return res.json()
    },
  })

  const { data: tpfgl } = useQuery<ApiResponse<Record<string, unknown>>>({
    queryKey: ["carbon", "tpfgl", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page1/tpfgl/${statType}`)
      return res.json()
    },
  })

  const { data: yjzl } = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page1", "yjzl", statType],
    queryFn: async () => {
      const res = await fetch(`/api/page1/yjzl/${statType}`)
      return res.json()
    },
  })

  const { data: zjyj } = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "page1", "zjyj"],
    queryFn: async () => {
      const res = await fetch("/api/page1/zjyj")
      return res.json()
    },
  })

  const info = ckInfo?.data ?? {}
  const s = stats?.data ?? ({} as Partial<MonitorStats>)
  const yd = ydfdzl?.data ?? {}
  const tf = tpfgl?.data ?? {}

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader
        eyebrow="态势总览"
        title="仓库碳管理大屏"
        description="企业信息、监测点位、用电发电与碳排放概览（与 xtck_deploy API 一致）"
      />

      <PageSection delay={0.1}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">统计粒度</div>
          <StatTypeSelect value={statType} onChange={setStatType} />
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>企业信息概况</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              {Object.entries(info).length === 0 ? (
                <div className="text-muted-foreground">暂无企业信息，请先在后端录入。</div>
              ) : (
                Object.entries(info).map(([k, v]) => (
                  <div key={k} className="flex justify-between">
                    <span className="text-muted-foreground">{k}</span>
                    <span>{String(v ?? "")}</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>监测点位在线统计</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-xs text-muted-foreground">用电总数</div>
                  <div className="text-xl font-semibold">{s.ydzs ?? "-"}</div>
                  <div className="text-xs text-muted-foreground">
                    在线 {s.ydzx ?? "-"} / 故障 {s.ydgz ?? "-"}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">发电总数</div>
                  <div className="text-xl font-semibold">{s.fdzs ?? "-"}</div>
                  <div className="text-xs text-muted-foreground">
                    在线 {s.fdzx ?? "-"} / 故障 {s.fdgz ?? "-"}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">视频总数</div>
                  <div className="text-xl font-semibold">{s.spzs ?? "-"}</div>
                  <div className="text-xs text-muted-foreground">
                    在线 {s.spzx ?? "-"} / 故障 {s.spgz ?? "-"}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection>
        <Tabs defaultValue="ydfd">
          <TabsList>
            <TabsTrigger value="ydfd">用电发电总览</TabsTrigger>
            <TabsTrigger value="tpf">碳排放概览</TabsTrigger>
            <TabsTrigger value="yj">预警概览</TabsTrigger>
          </TabsList>
          <TabsContent value="ydfd" className="space-y-2">
            <Card>
              <CardHeader>
                <CardTitle>用电发电总览（{statType === "day" ? "日" : statType === "month" ? "月" : "年"}）</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-6 text-sm">
                {Object.entries(yd).map(([k, v]) => (
                  <div key={k}>
                    <span className="text-muted-foreground">{k}: </span>
                    <span className="font-medium">{String(v ?? "-")}</span>
                  </div>
                ))}
                {Object.keys(yd).length === 0 && (
                  <div className="text-muted-foreground">暂无数据（依赖视图 yj_*_sum_view / hw_gf_*_sum_view）</div>
                )}
              </CardContent>
            </Card>
            <DataCard
              title={`用电发电企业排行 ydfdzl/qypx（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
              data={ydfdzlRank?.data ?? []}
            />
          </TabsContent>
          <TabsContent value="tpf" className="space-y-2">
            <Card>
              <CardHeader>
                <CardTitle>碳排放信息概览（{statType === "day" ? "日" : statType === "month" ? "月" : "年"}）</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-6 text-sm">
                {Object.entries(tf).map(([k, v]) => (
                  <div key={k}>
                    <span className="text-muted-foreground">{k}: </span>
                    <span className="font-medium">{String(v ?? "-")}</span>
                  </div>
                ))}
                {Object.keys(tf).length === 0 && (
                  <div className="text-muted-foreground">暂无数据</div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="yj" className="space-y-2">
            <div className="grid gap-6 md:grid-cols-2">
              <DataCard
                title={`预警质量 yjzl（${statType === "day" ? "日" : statType === "month" ? "月" : "年"}）`}
                data={yjzl?.data ?? {}}
              />
              <DataCard title="重点预警 zjyj" data={zjyj?.data ?? {}} />
            </div>
          </TabsContent>
        </Tabs>
      </PageSection>
    </PageContainer>
  )
}
