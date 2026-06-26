import type { View } from "../types";

type Props = {
  onNavigate: (view: View) => void;
  showBack?: boolean;
  onBack?: () => void;
};

export function SiteHeader({ onNavigate, showBack, onBack }: Props) {
  return (
    <header className="site-header">
      <div className="site-header__left">
        {showBack && onBack && (
          <button type="button" className="link-btn" onClick={onBack}>
            ← Floor plan
          </button>
        )}
        <span className="site-brand" onClick={() => onNavigate("blueprint")} role="button" tabIndex={0}>
          Atelier
        </span>
      </div>
      <nav className="site-nav">
        <button type="button" className="nav-link" onClick={() => onNavigate("about")}>
          About
        </button>
        <button type="button" className="nav-link nav-link--muted">
          Sign in
        </button>
      </nav>
    </header>
  );
}
