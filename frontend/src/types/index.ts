// ===================================
// User Types
// ===================================

export type UserRole = 'admin' | 'moderator' | 'user';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  full_name?: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  full_name?: string;
  password?: string;
}

// ===================================
// Auth Types
// ===================================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// ===================================
// Post Types
// ===================================

export interface AuthorInfo {
  id: number;
  username: string;
  full_name: string | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  order: number;
  is_active: boolean;
  created_at: string;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  slug: string;
  view_count: number;
  is_published: boolean;
  is_pinned: boolean;
  created_at: string;
  updated_at: string | null;
  author: AuthorInfo;
  category: Category | null;
  comment_count: number;
}

export interface PostCreate {
  title: string;
  content: string;
  category_id?: number;
  is_published?: boolean;
}

export interface PostUpdate {
  title?: string;
  content?: string;
  category_id?: number;
  is_published?: boolean;
  is_pinned?: boolean;
}

export interface PostListResponse {
  items: Post[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// ===================================
// Comment Types
// ===================================

export interface Comment {
  id: number;
  content: string;
  author: AuthorInfo;
  post_id: number;
  parent_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  replies: Comment[];
}

export interface CommentCreate {
  content: string;
  parent_id?: number;
}

export interface CommentUpdate {
  content: string;
}

// ===================================
// Dashboard Types
// ===================================

export interface DashboardStats {
  total_users: number;
  total_posts: number;
  total_comments: number;
  recent_users: User[];
  recent_posts: Post[];
}

// ===================================
// Menu Types
// ===================================

export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  href?: string;
  children?: MenuItem[];
  roles?: UserRole[];
}

// ===================================
// API Response Types
// ===================================

export interface ApiError {
  detail: string;
}

export interface PaginationParams {
  page?: number;
  size?: number;
  search?: string;
}

// ===================================
// Menu Types (API)
// ===================================

export interface Menu {
  id: number;
  name: string;
  url: string;
  icon: string | null;
  parent_id: number | null;
  order: number;
  is_active: boolean;
  required_role: string | null;
  created_at: string;
  children: Menu[];
}

export interface MenuCreate {
  name: string;
  url: string;
  icon?: string;
  parent_id?: number;
  order?: number;
  required_role?: string;
}

export interface MenuUpdate {
  name?: string;
  url?: string;
  icon?: string;
  parent_id?: number;
  order?: number;
  is_active?: boolean;
  required_role?: string;
}

export interface MenuTreeResponse {
  menus: Menu[];
}
