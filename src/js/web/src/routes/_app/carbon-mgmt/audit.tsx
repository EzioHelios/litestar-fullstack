/**
 * 碳业务审核操作日志 - 列表/筛选
 * API: /api/carbon/audit-logs
 */
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useMemo, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

type AuditRow = {
  id: number
  record_type: string
  record_id: number
  action: string
  operator_id?: string | null
  comment?: string | null
  created_at: string
}

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon-mgmt/audit")({
  component: AuditPage,
})

function AuditPage() {
  const [recordType, setRecordType] = useState<string>("all")
  const [action, setAction] = useState<string>("all")
  const [keyword, setKeyword] = useState("")

  const { data, isLoading, isError, refetch } = useQuery<ApiResponse<AuditRow[]>>({
    queryKey: ["carbon-mgmt", "audit", recordType, action],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (recordType !== "all") params.set("record_type", recordType)
      if (action !== "all") params.set("action", action)
      const res = await fetch(`/api/carbon/audit-logs?${params.toString()}`)
      return res.json()
    },
  })

  const rows = useMemo(() => {
    const raw = data?.data ?? []
    const kw = keyword.trim().toLowerCase()
    return raw.filter((r) => {
      if (!kw) return true
      const hay = `${r.record_type} ${r.record_id} ${r.comment ?? ""}`.toLowerCase()
      return hay.includes(kw)
    })
  }, [data?.data, keyword])

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader eyebrow="碳排放管理" title="审核操作日志" description="查看碳排放相关记录的送审/通过/驳回操作轨迹。" />
      <PageSection>
        <Card>
          <CardHeader className="space-y-3">
            <CardTitle>日志列表</CardTitle>
            <div className="flex flex-wrap items-center gap-3">
              <div className="w-[200px]">
                <Select value={recordType} onValueChange={setRecordType}>
                  <SelectTrigger>
                    <SelectValue placeholder="记录类型" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部类型</SelectItem>
                    <SelectItem value="Scope1MobileCombustion">Scope1MobileCombustion</SelectItem>
                    <SelectItem value="Scope1StationaryCombustion">Scope1StationaryCombustion</SelectItem>
                    <SelectItem value="Scope1RefrigerantLeak">Scope1RefrigerantLeak</SelectItem>
                    <SelectItem value="Scope2ElectricityBill">Scope2ElectricityBill</SelectItem>
                    <SelectItem value="Scope3WasteDisposal">Scope3WasteDisposal</SelectItem>
                    <SelectItem value="Scope3ThirdPartyTransport">Scope3ThirdPartyTransport</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="w-[160px]">
                <Select value={action} onValueChange={setAction}>
                  <SelectTrigger>
                    <SelectValue placeholder="操作" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部操作</SelectItem>
                    <SelectItem value="submit">submit</SelectItem>
                    <SelectItem value="approve">approve</SelectItem>
                    <SelectItem value="reject">reject</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="min-w-[260px] flex-1">
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索：记录ID/说明…" />
              </div>
              <button
                type="button"
                className="inline-flex h-9 items-center rounded-md border border-border/70 bg-secondary px-3 text-xs font-medium text-secondary-foreground hover:bg-secondary/80"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                查询
              </button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading && <div className="text-sm text-muted-foreground">正在加载…</div>}
            {isError && <div className="text-sm text-destructive">加载失败，请检查后端接口。</div>}
            {!isLoading && !isError && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>时间</TableHead>
                    <TableHead>记录类型</TableHead>
                    <TableHead>记录ID</TableHead>
                    <TableHead>操作</TableHead>
                    <TableHead>说明</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                        暂无数据
                      </TableCell>
                    </TableRow>
                  )}
                  {rows.map((r) => (
                    <TableRow key={r.id}>
                      <TableCell>{r.created_at}</TableCell>
                      <TableCell>{r.record_type}</TableCell>
                      <TableCell>{r.record_id}</TableCell>
                      <TableCell>
                        {r.action === "submit" && <Badge variant="secondary">送审</Badge>}
                        {r.action === "approve" && <Badge>通过</Badge>}
                        {r.action === "reject" && <Badge variant="destructive">驳回</Badge>}
                        {!["submit", "approve", "reject"].includes(r.action) && <Badge variant="outline">{r.action}</Badge>}
                      </TableCell>
                      <TableCell>{r.comment ?? "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </PageSection>
    </PageContainer>
  )
}

