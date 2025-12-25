'use client';

import { useEffect, useState } from 'react';
import { Plus, MoreHorizontal, Pencil, Trash2, ChevronRight, ChevronDown, GripVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { menuApi } from '@/lib/api';
import type { Menu, MenuCreate, MenuUpdate } from '@/types';

// 아이콘 옵션
const iconOptions = [
  { value: 'fa-dashboard', label: '대시보드' },
  { value: 'fa-list', label: '목록' },
  { value: 'fa-user', label: '사용자' },
  { value: 'fa-users', label: '사용자들' },
  { value: 'fa-cog', label: '설정' },
  { value: 'fa-shield', label: '보안' },
  { value: 'fa-file', label: '파일' },
  { value: 'fa-bars', label: '메뉴' },
];

// 역할 옵션
const roleOptions = [
  { value: '', label: '모든 사용자' },
  { value: 'user', label: '로그인 사용자' },
  { value: 'moderator', label: '중재자 이상' },
  { value: 'admin', label: '관리자만' },
];

interface MenuItemProps {
  menu: Menu;
  level: number;
  expandedMenus: Set<number>;
  onToggleExpand: (id: number) => void;
  onEdit: (menu: Menu) => void;
  onDelete: (menu: Menu) => void;
  parentMenus: Menu[];
}

function MenuItemRow({
  menu,
  level,
  expandedMenus,
  onToggleExpand,
  onEdit,
  onDelete,
}: MenuItemProps) {
  const hasChildren = menu.children && menu.children.length > 0;
  const isExpanded = expandedMenus.has(menu.id);

  return (
    <>
      <div
        className="flex items-center gap-2 py-2 px-3 border-b hover:bg-muted/50"
        style={{ paddingLeft: `${level * 24 + 12}px` }}
      >
        <GripVertical className="h-4 w-4 text-muted-foreground cursor-move" />

        {hasChildren ? (
          <button
            onClick={() => onToggleExpand(menu.id)}
            className="p-1 hover:bg-muted rounded"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : (
          <div className="w-6" />
        )}

        <div className="flex-1 flex items-center gap-3">
          <span className="font-medium">{menu.name}</span>
          <span className="text-sm text-muted-foreground">{menu.url}</span>
        </div>

        <div className="flex items-center gap-2">
          {menu.required_role && (
            <Badge variant="outline">{menu.required_role}</Badge>
          )}
          {!menu.is_active && (
            <Badge variant="secondary">비활성</Badge>
          )}
          <span className="text-sm text-muted-foreground">순서: {menu.order}</span>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(menu)}>
              <Pencil className="mr-2 h-4 w-4" />
              수정
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-red-500"
              onClick={() => onDelete(menu)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              삭제
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {hasChildren && isExpanded && (
        <>
          {menu.children.map((child) => (
            <MenuItemRow
              key={child.id}
              menu={child}
              level={level + 1}
              expandedMenus={expandedMenus}
              onToggleExpand={onToggleExpand}
              onEdit={onEdit}
              onDelete={onDelete}
              parentMenus={[]}
            />
          ))}
        </>
      )}
    </>
  );
}

export default function AdminMenusPage() {
  const [menus, setMenus] = useState<Menu[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedMenus, setExpandedMenus] = useState<Set<number>>(new Set());

  // 다이얼로그 상태
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedMenu, setSelectedMenu] = useState<Menu | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // 폼 상태
  const [formData, setFormData] = useState<MenuCreate & { is_active?: boolean }>({
    name: '',
    url: '',
    icon: '',
    parent_id: undefined,
    order: 0,
    required_role: '',
  });

  const fetchMenus = async () => {
    setLoading(true);
    try {
      const response = await menuApi.getMenuTree();
      setMenus(response.menus);
      // 모든 메뉴 펼치기
      const allIds = new Set<number>();
      const collectIds = (menuList: Menu[]) => {
        menuList.forEach((m) => {
          if (m.children && m.children.length > 0) {
            allIds.add(m.id);
            collectIds(m.children);
          }
        });
      };
      collectIds(response.menus);
      setExpandedMenus(allIds);
    } catch (err) {
      setError(err instanceof Error ? err.message : '메뉴 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMenus();
  }, []);

  const handleToggleExpand = (id: number) => {
    setExpandedMenus((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // 플랫 메뉴 목록 생성 (부모 선택용)
  const getFlatMenus = (menuList: Menu[], level = 0): { menu: Menu; level: number }[] => {
    const result: { menu: Menu; level: number }[] = [];
    menuList.forEach((menu) => {
      result.push({ menu, level });
      if (menu.children && menu.children.length > 0) {
        result.push(...getFlatMenus(menu.children, level + 1));
      }
    });
    return result;
  };

  const flatMenus = getFlatMenus(menus);

  const handleOpenCreate = () => {
    setSelectedMenu(null);
    setFormData({
      name: '',
      url: '',
      icon: '',
      parent_id: undefined,
      order: 0,
      required_role: '',
    });
    setEditDialogOpen(true);
  };

  const handleOpenEdit = (menu: Menu) => {
    setSelectedMenu(menu);
    setFormData({
      name: menu.name,
      url: menu.url,
      icon: menu.icon || '',
      parent_id: menu.parent_id || undefined,
      order: menu.order,
      required_role: menu.required_role || '',
      is_active: menu.is_active,
    });
    setEditDialogOpen(true);
  };

  const handleOpenDelete = (menu: Menu) => {
    setSelectedMenu(menu);
    setDeleteDialogOpen(true);
  };

  const handleSave = async () => {
    setActionLoading(true);
    try {
      if (selectedMenu) {
        // 수정
        const updateData: MenuUpdate = {
          name: formData.name,
          url: formData.url,
          icon: formData.icon || undefined,
          parent_id: formData.parent_id,
          order: formData.order,
          required_role: formData.required_role || undefined,
          is_active: formData.is_active,
        };
        await menuApi.update(selectedMenu.id, updateData);
      } else {
        // 생성
        const createData: MenuCreate = {
          name: formData.name,
          url: formData.url,
          icon: formData.icon || undefined,
          parent_id: formData.parent_id,
          order: formData.order,
          required_role: formData.required_role || undefined,
        };
        await menuApi.create(createData);
      }
      setEditDialogOpen(false);
      fetchMenus();
    } catch (err) {
      alert(err instanceof Error ? err.message : '저장에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedMenu) return;
    setActionLoading(true);
    try {
      await menuApi.delete(selectedMenu.id);
      setDeleteDialogOpen(false);
      setSelectedMenu(null);
      fetchMenus();
    } catch (err) {
      alert(err instanceof Error ? err.message : '삭제에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleInitDefault = async () => {
    if (!confirm('기본 메뉴를 추가하시겠습니까? 기존 메뉴는 유지됩니다.')) return;
    setActionLoading(true);
    try {
      await menuApi.initDefault();
      fetchMenus();
    } catch (err) {
      alert(err instanceof Error ? err.message : '초기화에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">메뉴 관리</h1>
          <p className="text-muted-foreground">사이드바 메뉴 구조를 관리하세요</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleInitDefault} disabled={actionLoading}>
            기본 메뉴 추가
          </Button>
          <Button onClick={handleOpenCreate}>
            <Plus className="mr-2 h-4 w-4" />
            새 메뉴
          </Button>
        </div>
      </div>

      {/* 에러 */}
      {error && (
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          {error}
        </div>
      )}

      {/* 메뉴 트리 */}
      <Card>
        <CardHeader>
          <CardTitle>메뉴 구조</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
          ) : menus.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
              <p>등록된 메뉴가 없습니다.</p>
              <Button variant="link" onClick={handleInitDefault}>
                기본 메뉴 추가하기
              </Button>
            </div>
          ) : (
            <div className="divide-y">
              {menus.map((menu) => (
                <MenuItemRow
                  key={menu.id}
                  menu={menu}
                  level={0}
                  expandedMenus={expandedMenus}
                  onToggleExpand={handleToggleExpand}
                  onEdit={handleOpenEdit}
                  onDelete={handleOpenDelete}
                  parentMenus={menus}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 편집 다이얼로그 */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{selectedMenu ? '메뉴 수정' : '새 메뉴 추가'}</DialogTitle>
            <DialogDescription>
              메뉴 정보를 입력하세요.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">메뉴 이름</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="대시보드"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="url">URL</Label>
              <Input
                id="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="/dashboard"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="icon">아이콘</Label>
              <Select
                value={formData.icon}
                onValueChange={(value) => setFormData({ ...formData, icon: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="아이콘 선택" />
                </SelectTrigger>
                <SelectContent>
                  {iconOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="parent">부모 메뉴</Label>
              <Select
                value={formData.parent_id?.toString() || ''}
                onValueChange={(value) =>
                  setFormData({ ...formData, parent_id: value ? parseInt(value) : undefined })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="최상위 메뉴" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">최상위 메뉴</SelectItem>
                  {flatMenus
                    .filter((item) => item.menu.id !== selectedMenu?.id)
                    .map((item) => (
                      <SelectItem key={item.menu.id} value={item.menu.id.toString()}>
                        {'—'.repeat(item.level)} {item.menu.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="order">순서</Label>
              <Input
                id="order"
                type="number"
                value={formData.order}
                onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">필요 권한</Label>
              <Select
                value={formData.required_role}
                onValueChange={(value) => setFormData({ ...formData, required_role: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="권한 선택" />
                </SelectTrigger>
                <SelectContent>
                  {roleOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedMenu && (
              <div className="flex items-center justify-between">
                <Label htmlFor="is_active">활성화</Label>
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              취소
            </Button>
            <Button onClick={handleSave} disabled={actionLoading || !formData.name || !formData.url}>
              {actionLoading ? '저장 중...' : '저장'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>메뉴 삭제</DialogTitle>
            <DialogDescription>
              정말로 &quot;{selectedMenu?.name}&quot; 메뉴를 삭제하시겠습니까?
              {selectedMenu?.children && selectedMenu.children.length > 0 && (
                <span className="block mt-2 text-red-500">
                  하위 메뉴 {selectedMenu.children.length}개도 함께 삭제됩니다.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              취소
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={actionLoading}>
              {actionLoading ? '삭제 중...' : '삭제'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
