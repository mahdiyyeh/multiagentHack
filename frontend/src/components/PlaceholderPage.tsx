import type { ReactNode } from "react";

type Props = {
  title: string;
  body: string;
  children?: ReactNode;
};

export function PlaceholderPage({ title, body, children }: Props) {
  return (
    <section className="placeholder-page">
      <p className="eyebrow">Atelier</p>
      <h2 className="section-title">{title}</h2>
      <p className="lede lede--narrow">{body}</p>
      {children}
    </section>
  );
}
