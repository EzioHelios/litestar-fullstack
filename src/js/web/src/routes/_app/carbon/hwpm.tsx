/**
 * 户外大屏 - 与 xtck_deploy API 对应：hwpm/show/num
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { DataCard } from "@/components/carbon/data-view"

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon/hwpm")({
  component: HwpmPage,
})

function HwpmPage() {
  const numQuery = useQuery<ApiResponse<unknown>>({
    queryKey: ["carbon", "hwpm", "show", "num"],
    queryFn: async () => {
      const res = await fetch("/api/hwpm/show/num")
      return res.json()
    },
  })

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader
        eyebrow="户外大屏"
        title="户外大屏展示"
        description="hwpm/show/num 接口数据（与 xtck_deploy 一致）"
      />
      <PageSection>
        {numQuery.isLoading && <div className="text-sm text-muted-foreground">正在加载数据…</div>}
        {numQuery.isError && <div className="text-sm text-destructive">数据加载失败，请检查后端接口或网络。</div>}
        <DataCard title="大屏展示数据 hwpm/show/num" data={numQuery.data?.data ?? {}} />
      </PageSection>
    </PageContainer>
  )
}
