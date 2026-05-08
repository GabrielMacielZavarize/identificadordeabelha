# BeeAI — Identidade Visual

Guia de marca do sistema de identificação inteligente de espécies de abelhas.

---

## Conceito da Marca

**BeeAI** une natureza e tecnologia em um nome direto e universal.

| Elemento | Significado |
|----------|-------------|
| **Bee** | Abelhas — o coração do projeto |
| **AI** | Inteligência artificial — a tecnologia por trás da classificação |
| **Clareza** | Qualquer pessoa entende: "IA para abelhas" |
| **Internacionalização** | Funciona em qualquer idioma |

**Tagline:** Identificação inteligente de espécies

---

## Paleta de Cores

### Cores Principais

| Nome | Hex | Variável CSS | Uso |
|------|-----|-------------|-----|
| Oxford Blue | `#2C4A6E` | `--primary` | Primária — navbar, headers, textos-chave |
| Dark Goldenrod | `#B8860B` | `--amber` | Acento — badges, ícones, botões, destaques |
| Forest Green | `#4A7C59` | `--green` | Científico — espécies, sucesso, labels |
| Parchment | `#F2EFE4` | `--background` | Background claro — tom acadêmico |

### Neutros

| Nome | Hex | Variável CSS | Uso |
|------|-----|-------------|-----|
| Near Black | `#1C1C1E` | `--ink` | Texto principal |
| Graphite | `#4A4A4F` | `--muted` | Texto secundário, legendas |
| Warm Stone | `#DDDBD0` | `--border` | Bordas, divisores |
| Pure White | `#FFFFFF` | `--surface` | Cards, modais, áreas de conteúdo |

### Semânticas

| Nome | Hex | Variável CSS | Uso |
|------|-----|-------------|-----|
| Deep Forest | `#3A6045` | `--green-dark` | Sucesso — identificação de alta confiança |
| Dark Amber | `#7A5900` | `--amber-dark` | Atenção — confiança média |
| Academic Red | `#8B1A1A` | `--danger` | Erro — confiança baixa, falha de upload |
| Deep Blue | `#1A3D6E` | `--blue` | Info — tooltips, links |

### Gradientes

```css
/* Botões primários */
background: linear-gradient(135deg, #B8860B 0%, #7A5900 100%);

/* Navbar / app header */
background: linear-gradient(180deg, #2C4A6E 0%, #1A2E4A 100%);

/* Título accent (landing page) */
background: linear-gradient(90deg, #B8860B 0%, #D4A017 45%, #B8860B 100%);
```

### Dark Mode (Landing Page)

| Elemento | Cor |
|----------|-----|
| Background | `#111827` |
| Cards | `#1E2D40` |
| Texto principal | `#E5E7EB` |
| Texto secundário | `#9CA3AF` |
| Bordas | `#243448` |
| Acento primário | `#B8860B` (Dark Goldenrod) |
| Científico | `#4A7C59` (Forest Green) |

---

## Tipografia

### Fontes

| Uso | Fonte | Peso | Tamanho |
|-----|-------|------|---------|
| Títulos / Logo | Outfit | SemiBold (600) | 28–48px |
| Subtítulos | Outfit | Medium (500) | 20–24px |
| Corpo de texto | Inter | Regular (400) | 14–16px |
| Labels / Badges | Inter | Medium (500) | 12–13px |
| Nomes científicos | Inter | Regular Italic (400i) | 14–16px |

Fonte carregada via Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600&family=Inter:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet" />
```

### Hierarquia (modo claro)

```
H1  — Outfit SemiBold 600, 40px,  Oxford Blue (#2C4A6E)
H2  — Outfit Medium 500,  28px,  Oxford Blue (#2C4A6E)
H3  — Outfit Medium 500,  22px,  Graphite (#4A4A4F)
Body — Inter Regular 400, 16px,  Near Black (#1C1C1E)
Caption — Inter Regular 400, 13px, Graphite (#4A4A4F)
Nomes científicos — Inter Italic 400, 14–16px
```

Nomes de espécies em itálico seguem a convenção científica: *Augochloropsis cupreola*

---

## Elementos Visuais

### Hexágonos
O hexágono (favo de mel) é o elemento geométrico principal da marca.

- Backgrounds com pattern sutil em baixa opacidade (4–6%)
- SVG `<pattern>` com hexágonos stroke em Forest Green
- Usado em: hero sections, fundos de cards de resultado

### Padrão de Rede Neural
Nós conectados por linhas finas, remetendo a redes neurais.

- Elemento decorativo do logo (`logosolucoesmobile.png`)
- Referência visual à camada técnica de IA

### Logo (`/public/logosolucoesmobile.png`)
Abelha estilizada com padrão de rede neural sobreposto ao abdômen.

| Contexto | Uso |
|----------|-----|
| App header | Logo no brand-mark (fundo branco, 48×48px) |
| Landing footer | Logo + texto "BeeAI" |
| Favicon | `logosolucoesmobile.png` como ícone da aba |
| Fundo escuro | Logo em card branco (preserva legibilidade do PNG) |

**Área de proteção:** margem mínima equivalente à altura da cabeça da abelha ao redor da logo em todas as direções.

---

## Componentes

### Navbar / App Header

```css
background: linear-gradient(180deg, #2C4A6E 0%, #1A2E4A 100%);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 8px;
```

Links: `rgba(255, 255, 255, 0.8)` | Ativo: `rgba(255, 255, 255, 0.18)` background + branco

### Botões

| Tipo | Estilo |
|------|--------|
| Primário | Gradiente Dark Goldenrod → Dark Amber, texto branco, `border-radius: 8–10px` |
| Secundário | Borda `1px solid #B8860B`, fundo transparente, texto `#B8860B` |
| Danger | Fundo `#8B1A1A`, texto branco |
| Hover | `translateY(-2px)` + `box-shadow: 0 4px 14px rgba(184,134,11,0.25)` |

### Cards (modo claro)

```css
border-radius: 14px;
border: 1px solid #DDDBD0;
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
background: rgba(255, 255, 255, 0.95);
```

### Inputs

```css
border-radius: 8px;
border: 1px solid #C9BEA9;
/* Focus ring */
outline: 3px solid rgba(184, 134, 11, 0.32);
```

### Confidence Meter

Gradiente `Dark Goldenrod → Forest Green` para barra de confiança — representa a transição de incerteza (âmbar) para precisão (verde científico).

---

## Tom de Voz

| Contexto | Tom |
|----------|-----|
| Interface / UI | Direto, claro, acolhedor |
| Resultados científicos | Preciso, confiável |
| Onboarding | Educativo, informativo |
| Erros | Empático, solucionador |

**Exemplos:**

- `"Identificamos uma Augochloropsis cupreola com 94% de confiança."`
- `"Envie uma foto da abelha para iniciar a análise."`
- Em vez de `"Erro 500: falha no processamento"` → `"Algo deu errado na análise. Tente enviar a foto novamente."`

---

## Modos de Exibição

### Light Mode (App — padrão)

| Elemento | Cor |
|----------|-----|
| Background | `#F2EFE4` (Parchment) |
| Cards | `#FFFFFF` com borda `#DDDBD0` |
| Texto | `#1C1C1E` (Near Black) |
| Navbar / Header | Oxford Blue `#2C4A6E` → `#1A2E4A` |
| Botão primário | Dark Goldenrod gradient |

### Dark Mode (Landing Page)

| Elemento | Cor |
|----------|-----|
| Background | `#111827` |
| Cards | `#1E2D40` |
| Texto | `#E5E7EB` |
| Acento | `#B8860B` (Dark Goldenrod) |
| Científico | `#4A7C59` (Forest Green) |

---

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `frontend/public/logosolucoesmobile.png` | Logo principal (PNG, fundo branco) |
| `frontend/public/favicon.svg` | Ícone bee SVG legado |
| `frontend/src/styles/globals.css` | Tokens de design (CSS custom properties) |
| `frontend/src/pages/LandingPage.css` | Estilos da landing page (dark mode) |
| `frontend/index.html` | Google Fonts + meta tags |
