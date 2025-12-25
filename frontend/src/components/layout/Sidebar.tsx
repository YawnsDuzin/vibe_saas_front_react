'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FileText,
  Users,
  Settings,
  X,
  Menu as MenuIcon,
  Shield,
  ChevronDown,
  ChevronRight,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { useAuthStore } from '@/stores/authStore';
import { useMenuStore } from '@/stores/menuStore';
import type { Menu } from '@/types';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

// 아이콘 매핑
const iconMap: Record<string, LucideIcon> = {
  'fa-dashboard': LayoutDashboard,
  'fa-list': FileText,
  'fa-user': Users,
  'fa-users': Users,
  'fa-cog': Settings,
  'fa-shield': Shield,
  'fa-file': FileText,
  'fa-bars': MenuIcon,
};

function MenuItemComponent({
  menu,
  pathname,
  onItemClick,
  level = 0,
  expandedMenus,
  onToggleExpand,
}: {
  menu: Menu;
  pathname: string;
  onItemClick?: () => void;
  level?: number;
  expandedMenus: Set<number>;
  onToggleExpand: (menuId: number) => void;
}) {
  const hasChildren = menu.children && menu.children.length > 0;
  const Icon = iconMap[menu.icon || ''] || FileText;
  const isActive = pathname === menu.url || pathname.startsWith(`${menu.url}/`);
  const isExpanded = expandedMenus.has(menu.id);

  if (hasChildren) {
    return (
      <div>
        <button
          onClick={() => onToggleExpand(menu.id)}
          className={cn(
            'flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
            isActive
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground',
            level > 0 && 'pl-6'
          )}
        >
          <span className="flex items-center gap-3">
            <Icon className="h-4 w-4" />
            {menu.name}
          </span>
          {isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </button>
        {isExpanded && (
          <div className="ml-2 mt-1">
            {menu.children.map((child) => (
              <MenuItemComponent
                key={child.id}
                menu={child}
                pathname={pathname}
                onItemClick={onItemClick}
                level={level + 1}
                expandedMenus={expandedMenus}
                onToggleExpand={onToggleExpand}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <Link
      href={menu.url}
      onClick={onItemClick}
      className={cn(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
        isActive
          ? 'bg-primary text-primary-foreground'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground',
        level > 0 && 'pl-6'
      )}
    >
      <Icon className="h-4 w-4" />
      {menu.name}
    </Link>
  );
}

function SidebarContent({ onItemClick }: { onItemClick?: () => void }) {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const { menus, isLoading: loading, fetchMenus } = useMenuStore();
  const [expandedMenus, setExpandedMenus] = useState<Set<number>>(new Set());

  // 메뉴 펼침/접기 토글
  const handleToggleExpand = (menuId: number) => {
    setExpandedMenus((prev) => {
      const next = new Set(prev);
      if (next.has(menuId)) {
        next.delete(menuId);
      } else {
        next.add(menuId);
      }
      return next;
    });
  };

  // 현재 경로에 해당하는 부모 메뉴를 자동으로 펼침
  const findParentMenuIds = (menuList: Menu[], path: string): number[] => {
    const ids: number[] = [];
    const findInMenu = (menu: Menu): boolean => {
      if (path.startsWith(menu.url)) {
        if (menu.children && menu.children.length > 0) {
          ids.push(menu.id);
          for (const child of menu.children) {
            findInMenu(child);
          }
        }
        return true;
      }
      return false;
    };
    for (const menu of menuList) {
      findInMenu(menu);
    }
    return ids;
  };

  useEffect(() => {
    // 스토어에 메뉴가 없으면 가져옴
    if (menus.length === 0) {
      fetchMenus();
    }
  }, [menus.length, fetchMenus]);

  // 메뉴 로드 후 현재 경로에 맞게 펼침
  useEffect(() => {
    if (menus.length > 0) {
      const parentIds = findParentMenuIds(menus, pathname);
      if (parentIds.length > 0) {
        setExpandedMenus((prev) => {
          const next = new Set(prev);
          parentIds.forEach((id) => next.add(id));
          return next;
        });
      }
    }
  }, [menus, pathname]);

  // 역할 기반 필터링
  const filteredMenus = menus.filter((menu) => {
    if (!menu.required_role) return true;
    if (!user) return false;
    if (menu.required_role === 'admin') return user.role === 'admin';
    if (menu.required_role === 'moderator') return ['admin', 'moderator'].includes(user.role);
    return true;
  });

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="grid gap-1 px-2">
          {filteredMenus.map((menu) => (
            <MenuItemComponent
              key={menu.id}
              menu={menu}
              pathname={pathname}
              onItemClick={onItemClick}
              expandedMenus={expandedMenus}
              onToggleExpand={handleToggleExpand}
            />
          ))}
        </nav>
      </div>
    </div>
  );
}

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* 데스크톱 사이드바 */}
      <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 md:pt-14 border-r bg-background">
        <SidebarContent />
      </aside>

      {/* 모바일 사이드바 */}
      <Sheet open={open} onOpenChange={onClose}>
        <SheetContent side="left" className="w-64 p-0">
          <div className="flex h-14 items-center justify-between border-b px-4">
            <span className="font-bold">메뉴</span>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <SidebarContent onItemClick={onClose} />
        </SheetContent>
      </Sheet>
    </>
  );
}
