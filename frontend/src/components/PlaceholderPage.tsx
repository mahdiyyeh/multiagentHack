type Props = {
  title: string;
  body: string;
};

export function PlaceholderPage({ title, body }: Props) {
  return (
    <section className="placeholder-page">
      <p className="eyebrow">Atelier</p>
      <h2 className="section-title">{title}</h2>
      <p className="lede lede--narrow">{body}</p>
    </section>
  );
}
