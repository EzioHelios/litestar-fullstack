/**
 * [Scope1] 固定源燃烧 - 列表/新增/送审/通过/驳回/删除
 * API: /api/carbon/scope1-stationary-combustion
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useMemo, useState } from "react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"

type Scope1Stationary = {
  id: number
  facility_name: string
  period_start: string
  period_end: string
  fuel_type: string
  amount: string | number
  unit: string
  meter_reading_start?: string | number | null
  meter_reading_end?: string | number | null
  attachment?: string | null
  remark?: string | null
  status?: string
  approved_at?: string | null
  reject_reason?: string | null
}

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon-mgmt/scope1-stationary")({
  component: Scope1StationaryPage,
})

function Scope1StationaryPage() {
  const qc = useQueryClient()
  const [keyword, setKeyword] = useState("")
  const [status, setStatus] = useState<string>("all")
  const [createOpen, setCreateOpen] = useState(false)

  const [form, setForm] = useState({
    facility_name: "",
    period_start: "",
    period_end: "",
    fuel_type: "diesel",
    amount: "",
    unit: "L",
    meter_reading_start: "",
    meter_reading_end: "",
    remark: "",
  })

  const listQuery = useQuery<ApiResponse<Scope1Stationary[]>>({
    queryKey: ["carbon-mgmt", "scope1-stationary", "list"],
    queryFn: async () => {
      const res = await fetch("/api/carbon/scope1-stationary-combustion")
      return res.json()
    },
  })

  const items = useMemo(() => {
    const raw = listQuery.data?.data ?? []
    const kw = keyword.trim().toLowerCase()
    return raw.filter((r) => {
      const okStatus = status === "all" ? true : (r.status ?? "draft") === status
      const hay = `${r.facility_name ?? ""} ${r.fuel_type ?? ""} ${r.unit ?? ""}`.toLowerCase()
      const okKw = kw.length === 0 ? true : hay.includes(kw)
      return okStatus && okKw
    })
  }, [keyword, listQuery.data?.data, status])

  const createMut = useMutation({
    mutationFn: async () => {
      const payload = {
        facility_name: form.facility_name,
        period_start: form.period_start,
        period_end: form.period_end,
        fuel_type: form.fuel_type,
        amount: form.amount,
        unit: form.unit,
        meter_reading_start: String(form.meter_reading_start).trim() ? form.meter_reading_start : null,
        meter_reading_end: String(form.meter_reading_end).trim() ? form.meter_reading_end : null,
        remark: form.remark || null,
      }
      const res = await fetch("/api/carbon/scope1-stationary-combustion", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      })
      const json = (await res.json()) as ApiResponse<Scope1Stationary>
      if (!res.ok) throw new Error(json.msg || "新增失败")
      return json.data
    },
    onSuccess: async () => {
      toast.success("新增成功")
      setCreateOpen(false)
      setForm({
        facility_name: "",
        period_start: "",
        period_end: "",
        fuel_type: "diesel",
        amount: "",
        unit: "L",
        meter_reading_start: "",
        meter_reading_end: "",
        remark: "",
      })
      await qc.invalidateQueries({ queryKey: ["carbon-mgmt", "scope1-stationary", "list"] })
    },
    onError: (e) => toast.error("新增失败", { description: e instanceof Error ? e.message : "请稍后重试" }),
  })

  const actionMut = useMutation({
    mutationFn: async (args: { id: number; action: "submit" | "approve" | "reject" | "delete" }) => {
      const { id, action } = args
      if (action === "delete") {
        const res = await fetch(`/api/carbon/scope1-stationary-combustion/${id}`, { method: "DELETE" })
        const json = (await res.json()) as ApiResponse<unknown>
        if (!res.ok) throw new Error(json.msg || "删除失败")
        return
      }
      const res = await fetch(`/api/carbon/scope1-stationary-combustion/${id}/${action}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: action === "reject" ? JSON.stringify({ reason: "不符合审核要求" }) : undefined,
      })
      const json = (await res.json()) as ApiResponse<unknown>
      if (!res.ok) throw new Error(json.msg || "操作失败")
    },
    onSuccess: async () => {
      toast.success("操作成功")
      await qc.invalidateQueries({ queryKey: ["carbon-mgmt", "scope1-stationary", "list"] })
    },
    onError: (e) => toast.error("操作失败", { description: e instanceof Error ? e.message : "请稍后重试" }),
  })

  function statusBadge(st?: string) {
    if (st === "approved") return <Badge>已通过</Badge>
    if (st === "pending") return <Badge variant="secondary">待审核</Badge>
    if (st === "rejected") return <Badge variant="destructive">已驳回</Badge>
    return <Badge variant="outline">草稿</Badge>
  }

  return (
    <PageContainer className="flex-1 space-y-6">
      <PageHeader eyebrow="碳排放管理" title="[Scope1] 固定源燃烧" description="固定源燃烧数据填报、审核流转与记录管理。" />

      <PageSection>
        <Card>
          <CardHeader className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <CardTitle>数据列表</CardTitle>
              <div className="flex flex-wrap gap-2">
                <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                  <DialogTrigger asChild>
                    <Button>新增</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>新增 - 固定源燃烧</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4">
                      <div className="grid gap-2">
                        <Label>设施名称</Label>
                        <Input value={form.facility_name} onChange={(e) => setForm((s) => ({ ...s, facility_name: e.target.value }))} placeholder="例如：食堂/锅炉/发电机" />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <Label>开始日期</Label>
                          <Input type="date" value={form.period_start} onChange={(e) => setForm((s) => ({ ...s, period_start: e.target.value }))} />
                        </div>
                        <div className="grid gap-2">
                          <Label>结束日期</Label>
                          <Input type="date" value={form.period_end} onChange={(e) => setForm((s) => ({ ...s, period_end: e.target.value }))} />
                        </div>
                      </div>
                      <div className="grid gap-2">
                        <Label>燃料类型</Label>
                        <Select value={form.fuel_type} onValueChange={(v) => setForm((s) => ({ ...s, fuel_type: v }))}>
                          <SelectTrigger>
                            <SelectValue placeholder="选择燃料类型" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="diesel">柴油</SelectItem>
                            <SelectItem value="gasoline">汽油</SelectItem>
                            <SelectItem value="lng">LNG</SelectItem>
                            <SelectItem value="cng">CNG</SelectItem>
                            <SelectItem value="natural_gas">天然气</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <Label>用量</Label>
                          <Input value={form.amount} onChange={(e) => setForm((s) => ({ ...s, amount: e.target.value }))} placeholder="例如：12.5" />
                        </div>
                        <div className="grid gap-2">
                          <Label>单位</Label>
                          <Input value={form.unit} onChange={(e) => setForm((s) => ({ ...s, unit: e.target.value }))} placeholder="L/kg/m³" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <Label>读数（开始）</Label>
                          <Input value={form.meter_reading_start} onChange={(e) => setForm((s) => ({ ...s, meter_reading_start: e.target.value }))} placeholder="可选" />
                        </div>
                        <div className="grid gap-2">
                          <Label>读数（结束）</Label>
                          <Input value={form.meter_reading_end} onChange={(e) => setForm((s) => ({ ...s, meter_reading_end: e.target.value }))} placeholder="可选" />
                        </div>
                      </div>
                      <div className="grid gap-2">
                        <Label>备注</Label>
                        <Textarea value={form.remark} onChange={(e) => setForm((s) => ({ ...s, remark: e.target.value }))} placeholder="可选" />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setCreateOpen(false)}>
                        取消
                      </Button>
                      <Button
                        onClick={() => createMut.mutate()}
                        disabled={
                          !form.facility_name.trim() ||
                          !form.period_start ||
                          !form.period_end ||
                          !form.fuel_type ||
                          !String(form.amount).trim() ||
                          !form.unit ||
                          createMut.isPending
                        }
                      >
                        保存
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                <Button variant="outline" onClick={() => (setKeyword(""), setStatus("all"))}>
                  重置
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="min-w-[260px] flex-1">
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索：设施名称/燃料类型/单位…" />
              </div>
              <div className="w-[160px]">
                <Select value={status} onValueChange={setStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="状态" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部状态</SelectItem>
                    <SelectItem value="draft">草稿</SelectItem>
                    <SelectItem value="pending">待审核</SelectItem>
                    <SelectItem value="approved">已通过</SelectItem>
                    <SelectItem value="rejected">已驳回</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button variant="secondary" onClick={() => listQuery.refetch()} disabled={listQuery.isFetching}>
                查询
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-3">
            {listQuery.isLoading && <div className="text-sm text-muted-foreground">正在加载…</div>}
            {listQuery.isError && <div className="text-sm text-destructive">加载失败，请检查后端接口。</div>}

            {!listQuery.isLoading && !listQuery.isError && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>设施名称</TableHead>
                    <TableHead>周期</TableHead>
                    <TableHead>燃料类型</TableHead>
                    <TableHead className="text-right">用量</TableHead>
                    <TableHead>单位</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead className="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                        暂无数据
                      </TableCell>
                    </TableRow>
                  )}
                  {items.map((r) => {
                    const st = r.status ?? "draft"
                    return (
                      <TableRow key={r.id}>
                        <TableCell>{r.facility_name}</TableCell>
                        <TableCell>
                          {r.period_start} ~ {r.period_end}
                        </TableCell>
                        <TableCell>{r.fuel_type}</TableCell>
                        <TableCell className="text-right">{String(r.amount)}</TableCell>
                        <TableCell>{r.unit}</TableCell>
                        <TableCell>{statusBadge(st)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex flex-wrap justify-end gap-2">
                            <Button variant="outline" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "submit" })} disabled={st !== "draft" || actionMut.isPending}>
                              送审
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "approve" })} disabled={st !== "pending" || actionMut.isPending}>
                              通过
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "reject" })} disabled={st !== "pending" || actionMut.isPending}>
                              驳回
                            </Button>
                            <Button variant="destructive" size="sm" onClick={() => actionMut.mutate({ id: r.id, action: "delete" })} disabled={st === "approved" || actionMut.isPending}>
                              删除
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </PageSection>
    </PageContainer>
  )
}

