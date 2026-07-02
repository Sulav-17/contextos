import {
  Archive,
  BookOpen,
  Brain,
  Home,
  MessagesSquare,
  Settings,
  Upload,
  type LucideIcon,
} from "lucide-react";

export type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  adminOnly?: boolean;
};

export const primaryNavItems: NavItem[] = [
  { href: "/home", label: "Home", icon: Home },
  { href: "/conversations", label: "Conversations", icon: MessagesSquare },
  { href: "/libraries", label: "Documents", icon: BookOpen },
  { href: "/memories", label: "Memories", icon: Brain },
] as const;

export const secondaryNavItems: NavItem[] = [
  { href: "/projects", label: "Projects", icon: Archive },
  { href: "/uploads", label: "Uploads", icon: Upload },
  { href: "/settings", label: "Settings", icon: Settings },
] as const;
