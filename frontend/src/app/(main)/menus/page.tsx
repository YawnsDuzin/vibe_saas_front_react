'use client';

import { useEffect, useState } from 'react';
import {
  Plus,
  MoreHorizontal,
  Pencil,
  Trash2,
  RefreshCw,
  GripVertical,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { menuApi } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import type { Menu, MenuCreate, MenuUpdate } from '@/types';
import { cn } from '@/lib/utils';

export default function MenusPage() {
  const { user: currentUser } = useAuthStore();
  const [menus, setMenus] = useState<Menu[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedMenu, setSelectedMenu] = useState<Menu | null>(null);

  // Form states
  const [formData, setFormData] = useState<MenuCreate>({
    name: '',
    url: '',
    icon: '',
    parent_id: undefined,
    order: 0,
    required_role: undefined,
  });

  const fetchMenus = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await menuApi.getMenuTree();
      setMenus(response.menus);
    } catch (err) {
      setError(err instanceof Error ? err.message : '메뉴 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMenus();
  }, []);

  const resetForm = () => {
    setFormData({
      name: '',
      url: '',
      icon: '',
      parent_id: undefined,
      order: 0,
      required_role: undefined,
    });
  };

  const handleCreate = async () => {
    if (!formData.name || !formData.url) {
      alert('메뉴 이름과 URL은 필수입니다.');
      return;
    }
    setActionLoading(true);
    try {
      await menuApi.create(formData);
      setCreateDialogOpen(false);
      resetForm();
      fetchMenus();
    } catch (err) {
      alert(err instanceof Error ? err.message : '메뉴 생성에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleEdit = async () => {
    if (!selectedMenu) return;
    setActionLoading(true);
    try {
      const updateData: MenuUpdate = {
        name: formData.name,
        url: formData.url,
        icon: formData.icon || undefined,
        order: formData.order,
        required_role: formData.required_role || undefined,
      };
      await menuApi.update(selectedMenu.id, updateData);
      setEditDialogOpen(false);
      setSelectedMenu(null);
      resetForm();
      fetchMenus();
    } catch (err) {
      alert(err instanceof Error ? err.message : '메뉴 수정에 실패했습니다.');
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
      alert(err instanceof Error ? err.message : '메뉴 삭제에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleInitDefault = async () => {
    if (!confirm('기본 메뉴를 초기화하시겠습니까? 기존 메뉴에 추가됩니다.')) return;
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

  const openEditDialog = (menu: Menu) => {
    setSelectedMenu(menu);
    setFormData({
      name: menu.name,
      url: menu.url,
      icon: menu.icon || '',
      parent_id: menu.parent_id || undefined,
      order: menu.order,
      required_role: menu.required_role || undefined,
    });
    setEditDialogOpen(true);
  };

  // 권한 체크
  if (!currentUser || currentUser.role !== 'admin') {
    return (
      <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
        관리자만 접근할 수 있습니다.
      </div>
    );
  }

  // 모든 메뉴를 평탄화 (부모 선택용)
  const flattenMenus = (menuList: Menu[], prefix = ''): { id: number; name: string }[] => {
    let result: { id: number; name: string }[] = [];
    for (const menu of menuList) {
      result.push({ id: menu.id, name: prefix + menu.name });
      if (menu.children && menu.children.length > 0) {
        result = [...result, ...flattenMenus(menu.children, prefix + '  ')];
      }
    }
    return result;
  };

  const allMenusFlat = flattenMenus(menus);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">메뉴 관리</h1>
          <p className="text-muted-foreground">사이드바 메뉴를 관리하세요</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleInitDefault} disabled={actionLoading}>
            <RefreshCw className="mr-2 h-4 w-4" />
            기본 메뉴 초기화
          </Button>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            메뉴 추가
          </Button>
        </div>
      </div>

      {/* 에러 */}
      {error && (
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          {error}
        </div>
      )}

      {/* 메뉴 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>메뉴 구조</CardTitle>
          <CardDescription>드래그하여 순서를 변경하거나 메뉴를 편집하세요</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
          ) : menus.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>등록된 메뉴가 없습니다.</p>
              <p className="text-sm mt-1">메뉴를 추가하거나 기본 메뉴를 초기화하세요.</p>
            </div>
          ) : (
            <MenuTree
              menus={menus}
              onEdit={openEditDialog}
              onDelete={(menu) => {
                setSelectedMenu(menu);
                setDeleteDialogOpen(true);
              }}
            />
          )}
        </CardContent>
      </Card>

      {/* 생성 다이얼로그 */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>메뉴 추가</DialogTitle>
            <DialogDescription>새로운 메뉴를 추가합니다.</DialogDescription>
          </DialogHeader>
          <MenuForm
            formData={formData}
            setFormData={setFormData}
            allMenus={allMenusFlat}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              취소
            </Button>
            <Button onClick={handleCreate} disabled={actionLoading}>
              {actionLoading ? '생성 중...' : '생성'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 수정 다이얼로그 */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>메뉴 수정</DialogTitle>
            <DialogDescription>메뉴 정보를 수정합니다.</DialogDescription>
          </DialogHeader>
          <MenuForm
            formData={formData}
            setFormData={setFormData}
            allMenus={allMenusFlat.filter((m) => m.id !== selectedMenu?.id)}
            isEdit
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              취소
            </Button>
            <Button onClick={handleEdit} disabled={actionLoading}>
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

// 메뉴 트리 컴포넌트
function MenuTree({
  menus,
  onEdit,
  onDelete,
  level = 0,
}: {
  menus: Menu[];
  onEdit: (menu: Menu) => void;
  onDelete: (menu: Menu) => void;
  level?: number;
}) {
  return (
    <div className={cn('space-y-1', level > 0 && 'ml-6 border-l pl-4')}>
      {menus.map((menu) => (
        <MenuTreeItem
          key={menu.id}
          menu={menu}
          onEdit={onEdit}
          onDelete={onDelete}
          level={level}
        />
      ))}
    </div>
  );
}

function MenuTreeItem({
  menu,
  onEdit,
  onDelete,
  level,
}: {
  menu: Menu;
  onEdit: (menu: Menu) => void;
  onDelete: (menu: Menu) => void;
  level: number;
}) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = menu.children && menu.children.length > 0;

  return (
    <div>
      <div className="flex items-center gap-2 py-2 px-3 rounded-lg hover:bg-muted group">
        <GripVertical className="h-4 w-4 text-muted-foreground cursor-grab" />
        {hasChildren ? (
          <button onClick={() => setExpanded(!expanded)} className="p-0.5">
            {expanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : (
          <div className="w-5" />
        )}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium">{menu.name}</span>
            <span className="text-sm text-muted-foreground">{menu.url}</span>
            {menu.required_role && (
              <Badge variant="secondary" className="text-xs">
                {menu.required_role}
              </Badge>
            )}
            {!menu.is_active && (
              <Badge variant="outline" className="text-xs">
                비활성
              </Badge>
            )}
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="opacity-0 group-hover:opacity-100"
            >
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
      {hasChildren && expanded && (
        <MenuTree
          menus={menu.children}
          onEdit={onEdit}
          onDelete={onDelete}
          level={level + 1}
        />
      )}
    </div>
  );
}

// 메뉴 폼 컴포넌트
function MenuForm({
  formData,
  setFormData,
  allMenus,
  isEdit = false,
}: {
  formData: MenuCreate;
  setFormData: (data: MenuCreate) => void;
  allMenus: { id: number; name: string }[];
  isEdit?: boolean;
}) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">메뉴 이름 *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="대시보드"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="url">URL *</Label>
        <Input
          id="url"
          value={formData.url}
          onChange={(e) => setFormData({ ...formData, url: e.target.value })}
          placeholder="/dashboard"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="icon">아이콘</Label>
        <Input
          id="icon"
          value={formData.icon}
          onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
          placeholder="fa-dashboard"
        />
        <p className="text-xs text-muted-foreground">
          사용 가능: fa-dashboard, fa-list, fa-user, fa-users, fa-cog, fa-shield, fa-file, fa-bars
        </p>
      </div>
      {!isEdit && (
        <div className="space-y-2">
          <Label htmlFor="parent">상위 메뉴</Label>
          <Select
            value={formData.parent_id?.toString() || 'none'}
            onValueChange={(value) =>
              setFormData({
                ...formData,
                parent_id: value === 'none' ? undefined : parseInt(value),
              })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="상위 메뉴 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">최상위 메뉴</SelectItem>
              {allMenus.map((menu) => (
                <SelectItem key={menu.id} value={menu.id.toString()}>
                  {menu.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}
      <div className="space-y-2">
        <Label htmlFor="order">정렬 순서</Label>
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
          value={formData.required_role || 'none'}
          onValueChange={(value) =>
            setFormData({
              ...formData,
              required_role: value === 'none' ? undefined : value,
            })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="권한 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">모든 사용자</SelectItem>
            <SelectItem value="user">로그인 사용자</SelectItem>
            <SelectItem value="moderator">중재자 이상</SelectItem>
            <SelectItem value="admin">관리자만</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
