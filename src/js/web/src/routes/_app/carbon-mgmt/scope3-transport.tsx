/**
 * [Scope3] 外购运输 - 列表/新增/送审/通过/驳回/删除
 * API: /api/carbon/scope3-third-party-transport
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

type Scope3Transport = {
  id: number
  waybill_no: string
  origin: string
  destination: string
  vehicle_type: string
  distance_km: string | number
  load_ton: string | number
  fuel_amount?: string | number | null
  attachment?: string | null
  remark?: string | null
  status?: string
  approved_at?: string | null
  reject_reason?: string | null
}

type ApiResponse<T> = { code: number; msg: string; data: T }

export const Route = createFileRoute("/_app/carbon-mgmt/scope3-transport")({
  component: Scope3TransportPage,
})

function Scope3TransportPage() {
  const qc = useQueryClient()
  const [keyword, setKeyword] = useState("")
  const [status, setStatus] = useState<string>("all")
  const [createOpen, setCreateOpen] = useState(false)

  const [form, setForm] = useState({
    waybill_no: "",
    origin: "",
    destination: "",
    vehicle_type: "",
    distance_km: "",
    load_ton: "",
    fuel_amount: "",
    remark: "",
  })

  const listQuery = useQuery<ApiResponse<Scope3Transport[]>>({
    queryKey: ["carbon-mgmt", "scope3-transport", "list"],
    queryFn: async () => {
      const res = await fetch("/api/carbon/scope3-third-party-transport")
      return res.json()
    },
  })

  const items = useMemo(() => {
    const raw = listQuery.data?.data ?? []
    const kw = keyword.trim().toLowerCase()
    return raw.filter((r) => {
      const okStatus = status === "all" ? true : (r.status ?? "draft") === status
      const hay = `${r.waybill_no ?? ""} ${r.origin ?? ""} ${r.destination ?? ""} ${r.vehicle_type ?? ""}`.toLowerCase()
      const okKw = kw.length === 0 ? true : hay.includes(kw)
      return okStatus && okKw
    })
  }, [keyword, listQuery.data?.data, status])

  const createMut = useMutation({
    mutationFn: async () => {
      const payload = {
        waybill_no: form.waybill_no,
        origin: form.origin,
        destination: form.destination,
        vehicle_type: form.vehicle_type,
        distance_km: form.distance_km,
        load_ton: form.load_ton,
        fuel_amount: String(form.fuel_amount).trim() ? form.fuel_amount : null,
        remark: form.remark || null,
      }
      const res = await fetch("/api/carbon/scope3-third-party-transport", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      })
      const json = (await res.json()) as ApiResponse<Scope3Transport>
      if (!res.ok) throw new Error(json.msg || "新增失败")
      return json.data
    },
    onSuccess: async () => {
      toast.success("新增成功")
      setCreateOpen(false)
      setForm({ waybill_no: "", origin: "", destination: "", vehicle_type: "", distance_km: "", load_ton: "", fuel_amount: "", remark: "" })
      await qc.invalidateQueries({ queryKey: ["carbon-mgmt", "scope3-transport", "list"] })
    },
    onError: (e) => toast.error("新增失败", { description: e instanceof Error ? e.message : "请稍后重试" }),
  })

  const actionMut = useMutation({
    mutationFn: async (args: { id: number; action: "submit" | "approve" | "reject" | "delete" }) => {
      const { id, action } = args
      if (action === "delete") {
        const res = await fetch(`/api/carbon/scope3-third-party-transport/${id}`, { method: "DELETE" })
        const json = (await res.json()) as ApiResponse<unknown>
        if (!res.ok) throw new Error(json.msg || "删除失败")
        return
      }
      const res = await fetch(`/api/carbon/scope3-third-party-transport/${id}/${action}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: action === "reject" ? JSON.stringify({ reason: "不符合审核要求" }) : undefined,
      })
      const json = (await res.json()) as ApiResponse<unknown>
      if (!res.ok) throw new Error(json.msg || "操作失败")
    },
    onSuccess: async () => {
      toast.success("操作成功")
      await qc.invalidateQueries({ queryKey: ["carbon-mgmt", "scope3-transport", "list"] })
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
      <PageHeader eyebrow="碳排放管理" title="[Scope3] 外购运输" description="外购运输数据填报、审核流转与记录管理。" />

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
                      <DialogTitle>新增 - 外购运输</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4">
                      <div className="grid gap-2">
                        <Label>运单号</Label>
                        <Input value={form.waybill_no} onChange={(e) => setForm((s) => ({ ...s, waybill_no: e.target.value }))} placeholder="例如：WB20260301001" />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <Label>起点</Label>
                          <Input value={form.origin} onChange={(e) => setForm((s) => ({ ...s, origin: e.target.value }))} placeholder="例如：园区A" />
                        </div>
                        <div className="grid gap-2">
                          <Label>终点</Label>
                          <Input value={form.destination} onChange={(e) => setForm((s) => ({ ...s, destination: e.target.value }))} placeholder="例如：园区B" />
                        </div>
                      </div>
                      <div className="grid gap-2">
                        <Label>车辆类型</Label>
                        <Input value={form.vehicle_type} onChange={(e) => setForm((s) => ({ ...s, vehicle_type: e.target.value }))} placeholder="例如：轻卡/重卡" />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-2">
                          <Label>距离(km)</Label>
                          <Input value={form.distance_km} onChange={(e) => setForm((s) => ({ ...s, distance_km: e.target.value }))} placeholder="例如：35.5" />
                        </div>
                        <div className="grid gap-2">
                          <Label>载重(吨)</Label>
                          <Input value={form.load_ton} onChange={(e) => setForm((s) => ({ ...s, load_ton: e.target.value }))} placeholder="例如：12.0" />
                        </div>
                      </div>
                      <div className="grid gap-2">
                        <Label>燃料用量</Label>
                        <Input value={form.fuel_amount} onChange={(e) => setForm((s) => ({ ...s, fuel_amount: e.target.value }))} placeholder="可选" />
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
                          !form.waybill_no.trim() ||
                          !form.origin.trim() ||
                          !form.destination.trim() ||
                          !form.vehicle_type.trim() ||
                          !String(form.distance_km).trim() ||
                          !String(form.load_ton).trim() ||
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
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索：运单号/起点/终点/车辆类型…" />
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
                    <TableHead>运单号</TableHead>
                    <TableHead>起点</TableHead>
                    <TableHead>终点</TableHead>
                    <TableHead className="text-right">距离(km)</TableHead>
                    <TableHead className="text-right">载重(吨)</TableHead>
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
                        <TableCell>{r.waybill_no}</TableCell>
                        <TableCell>{r.origin}</TableCell>
                        <TableCell>{r.destination}</TableCell>
                        <TableCell className="text-right">{String(r.distance_km)}</TableCell>
                        <TableCell className="text-right">{String(r.load_ton)}</TableCell>
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

