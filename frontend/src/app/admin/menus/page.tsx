'use client';

import { useEffect, useState, useMemo } from 'react';
import { Plus, MoreHorizontal, Pencil, Trash2, ChevronRight, ChevronDown, GripVertical } from 'lucide-react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
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
import { useMenuStore } from '@/stores/menuStore';
import type { Menu, MenuCreate, MenuUpdate, MenuOrderItem } from '@/types';

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

// 역할 옵션 (빈 문자열은 Select에서 사용 불가하므로 '__none__' 사용)
const NONE_VALUE = '__none__';

const roleOptions = [
  { value: NONE_VALUE, label: '모든 사용자' },
  { value: 'user', label: '로그인 사용자' },
  { value: 'moderator', label: '중재자 이상' },
  { value: 'admin', label: '관리자만' },
];

// 플랫 메뉴 아이템 (드래그 앤 드롭용)
interface FlatMenuItem {
  menu: Menu;
  level: number;
  parentId: number | null;
}

interface SortableMenuItemProps {
  item: FlatMenuItem;
  expandedMenus: Set<number>;
  onToggleExpand: (id: number) => void;
  onEdit: (menu: Menu) => void;
  onDelete: (menu: Menu) => void;
}

function SortableMenuItem({
  item,
  expandedMenus,
  onToggleExpand,
  onEdit,
  onDelete,
}: SortableMenuItemProps) {
  const { menu, level } = item;
  const hasChildren = menu.children && menu.children.length > 0;
  const isExpanded = expandedMenus.has(menu.id);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: menu.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-2 py-2 px-3 border-b hover:bg-muted/50 ${isDragging ? 'bg-muted' : ''}`}
    >
      <div style={{ paddingLeft: `${level * 24}px` }} className="flex items-center gap-2">
        <button
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing touch-none"
        >
          <GripVertical className="h-4 w-4 text-muted-foreground" />
        </button>

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
      </div>

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
  );
}

// 드래그 오버레이용 컴포넌트
function DragOverlayItem({ menu, level }: { menu: Menu; level: number }) {
  return (
    <div
      className="flex items-center gap-2 py-2 px-3 border rounded-lg bg-background shadow-lg"
      style={{ paddingLeft: `${level * 24 + 12}px` }}
    >
      <GripVertical className="h-4 w-4 text-muted-foreground" />
      <div className="w-6" />
      <div className="flex-1 flex items-center gap-3">
        <span className="font-medium">{menu.name}</span>
        <span className="text-sm text-muted-foreground">{menu.url}</span>
      </div>
    </div>
  );
}

export default function AdminMenusPage() {
  const [menus, setMenus] = useState<Menu[]>([]);
  const [loading, setLoading] = useState(true);
  const { setMenus: setGlobalMenus } = useMenuStore();
  const [error, setError] = useState<string | null>(null);
  const [expandedMenus, setExpandedMenus] = useState<Set<number>>(new Set());
  const [activeId, setActiveId] = useState<number | null>(null);

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

  // DnD 센서 설정
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // 플랫 메뉴 목록 생성 (드래그 앤 드롭용)
  const flatMenuItems = useMemo(() => {
    const result: FlatMenuItem[] = [];

    const flatten = (menuList: Menu[], level: number, parentId: number | null) => {
      menuList.forEach((menu) => {
        result.push({ menu, level, parentId });
        if (menu.children && menu.children.length > 0 && expandedMenus.has(menu.id)) {
          flatten(menu.children, level + 1, menu.id);
        }
      });
    };

    flatten(menus, 0, null);
    return result;
  }, [menus, expandedMenus]);

  // 플랫 메뉴 ID 목록
  const flatMenuIds = useMemo(() => flatMenuItems.map((item) => item.menu.id), [flatMenuItems]);

  const fetchMenus = async () => {
    setLoading(true);
    try {
      const response = await menuApi.getMenuTree();
      setMenus(response.menus);
      setGlobalMenus(response.menus); // 전역 상태도 업데이트
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

  const flatMenusForSelect = getFlatMenus(menus);

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

  // 드래그 시작
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as number);
  };

  // 드래그 종료 및 순서 업데이트
  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over || active.id === over.id) return;

    const oldIndex = flatMenuItems.findIndex((item) => item.menu.id === active.id);
    const newIndex = flatMenuItems.findIndex((item) => item.menu.id === over.id);

    if (oldIndex === -1 || newIndex === -1) return;

    const draggedItem = flatMenuItems[oldIndex];
    const targetItem = flatMenuItems[newIndex];

    // 같은 레벨에서만 이동 가능 (같은 부모를 가진 메뉴끼리)
    if (draggedItem.parentId !== targetItem.parentId) {
      // 다른 그룹으로 이동하는 경우, 해당 그룹의 마지막 순서로 이동
      const newParentId = targetItem.parentId;

      // 같은 부모를 가진 메뉴들 찾기
      const siblingsInTargetGroup = flatMenuItems.filter(
        (item) => item.parentId === newParentId
      );

      // 새로운 순서 계산
      const items: MenuOrderItem[] = [];

      // 이동하는 메뉴의 새 순서 및 부모 설정
      const targetIndex = siblingsInTargetGroup.findIndex(
        (item) => item.menu.id === over.id
      );

      // 같은 그룹 내 메뉴들의 순서 재조정
      siblingsInTargetGroup.forEach((item, index) => {
        if (item.menu.id === over.id) {
          // 드래그한 아이템을 여기에 삽입
          items.push({
            id: draggedItem.menu.id,
            order: index,
            parent_id: newParentId === null ? 0 : newParentId,
          });
          items.push({
            id: item.menu.id,
            order: index + 1,
            parent_id: newParentId === null ? 0 : newParentId,
          });
        } else if (item.menu.id !== draggedItem.menu.id) {
          const newOrder = index + (targetIndex !== -1 && index > targetIndex ? 1 : 0);
          if (item.menu.order !== newOrder) {
            items.push({
              id: item.menu.id,
              order: newOrder,
              parent_id: newParentId === null ? 0 : newParentId,
            });
          }
        }
      });

      // 드래그한 아이템이 기존 그룹에서 빠지면서 순서 재조정
      const originalSiblings = flatMenuItems.filter(
        (item) => item.parentId === draggedItem.parentId && item.menu.id !== draggedItem.menu.id
      );
      originalSiblings.forEach((item, index) => {
        if (item.menu.order !== index) {
          // 이미 추가된 아이템이 아닌 경우에만 추가
          const existingItem = items.find((i) => i.id === item.menu.id);
          if (!existingItem) {
            items.push({
              id: item.menu.id,
              order: index,
            });
          }
        }
      });

      if (items.length > 0) {
        try {
          setActionLoading(true);
          const response = await menuApi.reorder({ items });
          setMenus(response.menus);
          setGlobalMenus(response.menus); // 전역 상태도 업데이트
        } catch (err) {
          alert(err instanceof Error ? err.message : '순서 변경에 실패했습니다.');
          fetchMenus();
        } finally {
          setActionLoading(false);
        }
      }
    } else {
      // 같은 그룹 내에서 이동
      const siblings = flatMenuItems.filter(
        (item) => item.parentId === draggedItem.parentId
      );
      const siblingOldIndex = siblings.findIndex(
        (item) => item.menu.id === active.id
      );
      const siblingNewIndex = siblings.findIndex(
        (item) => item.menu.id === over.id
      );

      const newSiblings = arrayMove(siblings, siblingOldIndex, siblingNewIndex);

      // 순서 업데이트
      const items: MenuOrderItem[] = newSiblings.map((item, index) => ({
        id: item.menu.id,
        order: index,
      }));

      try {
        setActionLoading(true);
        const response = await menuApi.reorder({ items });
        setMenus(response.menus);
        setGlobalMenus(response.menus); // 전역 상태도 업데이트
      } catch (err) {
        alert(err instanceof Error ? err.message : '순서 변경에 실패했습니다.');
        fetchMenus();
      } finally {
        setActionLoading(false);
      }
    }
  };

  // 활성 아이템 찾기
  const activeItem = activeId
    ? flatMenuItems.find((item) => item.menu.id === activeId)
    : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">메뉴 관리</h1>
          <p className="text-muted-foreground">사이드바 메뉴 구조를 관리하세요. 드래그하여 순서를 변경할 수 있습니다.</p>
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
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
            >
              <SortableContext items={flatMenuIds} strategy={verticalListSortingStrategy}>
                <div className="divide-y">
                  {flatMenuItems.map((item) => (
                    <SortableMenuItem
                      key={item.menu.id}
                      item={item}
                      expandedMenus={expandedMenus}
                      onToggleExpand={handleToggleExpand}
                      onEdit={handleOpenEdit}
                      onDelete={handleOpenDelete}
                    />
                  ))}
                </div>
              </SortableContext>
              <DragOverlay>
                {activeItem ? (
                  <DragOverlayItem menu={activeItem.menu} level={activeItem.level} />
                ) : null}
              </DragOverlay>
            </DndContext>
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
                value={formData.icon || NONE_VALUE}
                onValueChange={(value) => setFormData({ ...formData, icon: value === NONE_VALUE ? '' : value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="아이콘 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE_VALUE}>선택 안함</SelectItem>
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
                value={formData.parent_id?.toString() || NONE_VALUE}
                onValueChange={(value) =>
                  setFormData({ ...formData, parent_id: value && value !== NONE_VALUE ? parseInt(value) : undefined })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="최상위 메뉴" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE_VALUE}>최상위 메뉴</SelectItem>
                  {flatMenusForSelect
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
                value={formData.required_role || NONE_VALUE}
                onValueChange={(value) => setFormData({ ...formData, required_role: value === NONE_VALUE ? '' : value })}
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
