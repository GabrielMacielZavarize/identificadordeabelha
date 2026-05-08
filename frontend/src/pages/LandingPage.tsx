import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './LandingPage.css'

// ── Core SVG components ────────────────────────────────────────────────────────

function BeeIcon({ size = 32, color = '#B8860B' }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <ellipse cx="16" cy="18" rx="8" ry="10" fill={color} opacity=".9" />
      <rect x="10" y="13" width="12" height="3" rx="1.5" fill="#0b1c13" opacity=".35" />
      <rect x="10" y="18" width="12" height="3" rx="1.5" fill="#0b1c13" opacity=".35" />
      <ellipse cx="16" cy="10" rx="5" ry="4" fill={color} opacity=".75" />
      <ellipse cx="9" cy="12" rx="5" ry="2.5" fill="white" opacity=".18" transform="rotate(-30 9 12)" />
      <ellipse cx="23" cy="12" rx="5" ry="2.5" fill="white" opacity=".18" transform="rotate(30 23 12)" />
      <circle cx="14" cy="9" r="1" fill="#0b1c13" opacity=".5" />
      <circle cx="18" cy="9" r="1" fill="#0b1c13" opacity=".5" />
    </svg>
  )
}

function HoneycombBg({ opacity = 0.06 }: { opacity?: number }) {
  return (
    <svg
      aria-hidden="true"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', opacity }}
    >
      <defs>
        <pattern id="hex" x="0" y="0" width="56" height="64" patternUnits="userSpaceOnUse">
          <polygon points="28,2 54,16 54,48 28,62 2,48 2,16" fill="none" stroke="#4A7C59" strokeWidth="1" />
          <polygon points="28,34 54,48 54,80 28,94 2,80 2,48" fill="none" stroke="#4A7C59" strokeWidth="1" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#hex)" />
    </svg>
  )
}

function Check() {
  return (
    <svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true">
      <path d="M1 4l3 3L9 1" stroke="#4A7C59" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function ArrowRight({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// ── Card icons ─────────────────────────────────────────────────────────────────

function IconDiploma() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="1.5" y="1.5" width="15" height="11" rx="1.5" />
      <path d="M5 6.5h8M5 9.5h5" />
      <path d="M6.5 12.5v4l2.5-1.5 2.5 1.5v-4" />
    </svg>
  )
}

function IconNetwork() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="9" cy="9" r="2.5" />
      <circle cx="3" cy="4.5" r="1.5" />
      <circle cx="15" cy="4.5" r="1.5" />
      <circle cx="9" cy="15.5" r="1.5" />
      <path d="M4.5 5.5l3 2.5M13.5 5.5l-3 2.5M9 11.5v2.5" />
    </svg>
  )
}

function IconBarChart() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3.5 14.5V9.5M7 14.5V6M10.5 14.5V11M14.5 14.5V4" />
      <path d="M1.5 14.5h15" />
    </svg>
  )
}

// ── Dados ──────────────────────────────────────────────────────────────────────

const SPECIES_GROUPS = [
  {
    model: 'DINOv2',
    label: 'Augochloropsis',
    sublabel: 'Classificador específico treinado com imagens do gênero',
    color: '#4A7C59',
    badge: 'Modelo específico',
    species: [
      { sci: 'Augochloropsis metallica', common: 'abelha verde metálica' },
      { sci: 'Augochloropsis ignita',    common: 'abelha verde' },
    ],
  },
  {
    model: 'CLIP',
    label: 'Identificação geral',
    sublabel: 'Modelo zero-shot para identificação de outras espécies',
    color: '#B8860B',
    badge: 'Modelo global',
    species: [
      { sci: 'Apis mellifera',      common: 'abelha-do-mel' },
      { sci: 'Bombus impatiens',    common: 'mamangaba' },
      { sci: 'Xylocopa virginica',  common: 'abelha carpinteira' },
      { sci: 'Halictus ligatus',    common: 'abelha de suor' },
      { sci: 'Vespula vulgaris',    common: 'vespa comum' },
    ],
  },
]

// ── Landing Page ───────────────────────────────────────────────────────────────

export function LandingPage() {
  const [ready, setReady] = useState(false)
  const [barReady, setBarReady] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setReady(true), 80)

    const scrollEls = document.querySelectorAll(
      '.lp-reveal, .lp-reveal-left, .lp-reveal-right, .lp-stagger'
    )
    const scrollObs = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('lp-visible')
            scrollObs.unobserve(e.target)
          }
        }),
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    )
    scrollEls.forEach((el) => scrollObs.observe(el))

    const mockEl = document.getElementById('lp-mock-bar')
    if (mockEl) {
      const barObs = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setBarReady(true)
            barObs.disconnect()
          }
        },
        { threshold: 0.4 }
      )
      barObs.observe(mockEl)
    }

    return () => {
      clearTimeout(t)
      scrollObs.disconnect()
    }
  }, [])

  return (
    <div className="lp-root">

      {/* ── Hero ────────────────────────────────────────────────────────────── */}
      <section className="lp-hero" aria-labelledby="hero-title">
        <HoneycombBg opacity={0.05} />

        <div className="lp-hero-inner">
          {/* Left — text */}
          <div className={`lp-hero-text${ready ? ' lp-ready' : ''}`}>
            <h1 id="hero-title" className="lp-hero-title">
              Identificação automática de{' '}
              <em className="lp-hero-title-accent">espécies de abelhas</em>
            </h1>

            <p className="lp-hero-sub">
              Sistema de visão computacional que usa <strong style={{ color: '#E5E7EB' }}>DINOv2</strong> e{' '}
              <strong style={{ color: '#E5E7EB' }}>CLIP</strong> para classificar espécies de abelhas
              a partir de fotografias, com score de confiança por classe.
            </p>

            <div className="lp-hero-actions">
              <Link to="/app" className="lp-btn-primary">
                Classificar imagem <ArrowRight />
              </Link>
              <a href="#species" className="lp-btn-secondary">
                Ver espécies
              </a>
            </div>

            <div className="lp-hero-divider" aria-hidden="true" />

            <div className="lp-hero-stats">
              {[
                { value: '> 90%',  label: 'Acurácia top-1' },
                { value: '7',      label: 'Espécies identificadas' },
                { value: '< 3 s',  label: 'Tempo de inferência' },
              ].map((s) => (
                <div key={s.label} className="lp-hero-stat">
                  <span className="lp-hero-stat-value">{s.value}</span>
                  <span className="lp-hero-stat-label">{s.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right — mock result card */}
          <div className={`lp-hero-visual${ready ? ' lp-ready' : ''}`}>
            <div className="lp-float-badge lp-float-badge-1" aria-hidden="true">
              &lt; 3 s · inferência
            </div>
            <div className="lp-float-badge lp-float-badge-2" aria-hidden="true">
              94.2% · confiança
            </div>

            <div className="lp-mock-card" id="lp-mock-bar">
              <div className="lp-mock-header">
                <div className="lp-mock-dot" style={{ background: '#ff5f57' }} />
                <div className="lp-mock-dot" style={{ background: '#febc2e' }} />
                <div className="lp-mock-dot" style={{ background: '#28c840' }} />
                <span className="lp-mock-header-title">análise da imagem</span>
              </div>

              <div className="lp-mock-body">
                <div className="lp-mock-image-area">
                  <HoneycombBg opacity={0.1} />
                  <div className="lp-mock-bee-wrap">
                    <BeeIcon size={72} color="#B8860B" />
                    <span className="lp-mock-bee-label">amostra analisada</span>
                  </div>
                </div>

                <div className="lp-mock-result">
                  <span className="lp-mock-result-eyebrow">Espécie identificada</span>
                  <span className="lp-mock-result-name">Augochloropsis ignita</span>

                  <div className="lp-mock-confidence-row">
                    <div className="lp-mock-bar-track">
                      <div
                        className={`lp-mock-bar-fill${barReady ? ' lp-bar-ready' : ''}`}
                        style={{ transition: 'width 1.6s .4s cubic-bezier(.22,.61,.36,1)' }}
                      />
                    </div>
                    <span className="lp-mock-bar-pct">94.2%</span>
                  </div>
                </div>

                <div className="lp-mock-species-list">
                  {[
                    { name: 'A. ignita',      pct: '94.2%', w: '94%' },
                    { name: 'A. patens',      pct: '3.8%',  w: '38%' },
                    { name: 'A. semiviridia', pct: '1.6%',  w: '16%' },
                  ].map((sp) => (
                    <div key={sp.name} className="lp-mock-species-row">
                      <span style={{ minWidth: 105 }}>{sp.name}</span>
                      <div className="lp-mock-species-bar">
                        <div
                          className="lp-mock-species-fill"
                          style={{ '--w': sp.w, width: barReady ? sp.w : 0 } as React.CSSProperties}
                        />
                      </div>
                      <span className="lp-mock-species-pct">{sp.pct}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Problem ─────────────────────────────────────────────────────────── */}
      <section className="lp-section lp-section-alt" id="problem" aria-labelledby="problem-title">
        <HoneycombBg opacity={0.04} />
        <div className="lp-section-inner">
          <div className="lp-reveal">
            <div className="lp-eyebrow lp-eyebrow-amber">O Problema</div>
            <h2 id="problem-title" className="lp-section-title">
              Classificação manual: cara, lenta e dependente de especialistas
            </h2>
            <p className="lp-section-sub">
              Identificar espécies de abelhas exige expertise especializada,
              microscópio e horas de análise, tornando o processo não escalável.
            </p>
          </div>

          <div className="lp-problem-grid lp-stagger">
            {[
              {
                num: '01',
                title: 'Exige microscópio especializado',
                desc: 'Diferenças morfológicas sutis só são visíveis com equipamento óptico de alta precisão.',
              },
              {
                num: '02',
                title: 'Processo demorado',
                desc: 'Cada identificação manual pode levar minutos a horas, inviabilizando análises em larga escala.',
              },
              {
                num: '03',
                title: 'Dependência de especialistas',
                desc: 'A expertise taxonômica é escassa. Um pesquisador vira gargalo para toda a pipeline.',
              },
              {
                num: '04',
                title: 'Não escalável',
                desc: 'Estudos de biodiversidade precisam de milhares de classificações, impossível manualmente.',
              },
            ].map((item) => (
              <div key={item.title} className="lp-card lp-card-amber">
                <span className="lp-card-num">{item.num}</span>
                <h3 className="lp-card-title">{item.title}</h3>
                <p className="lp-card-desc">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Models ──────────────────────────────────────────────────────────── */}
      <section className="lp-section" id="models" aria-labelledby="models-title">
        <HoneycombBg opacity={0.04} />
        <div className="lp-section-inner">
          <div className="lp-reveal">
            <div className="lp-eyebrow lp-eyebrow-green">Modelos</div>
            <h2 id="models-title" className="lp-section-title">Dois modelos complementares</h2>
            <p className="lp-section-sub">
              Um classificador específico treinado para Augochloropsis e um modelo zero-shot
              para identificação geral de espécies.
            </p>
          </div>

          <div className="lp-models-grid lp-stagger">
            {/* DINOv2 */}
            <div className="lp-model-card">
              <div className="lp-model-header">
                <span className="lp-model-badge lp-model-badge-green">DINOv2</span>
                <h3 className="lp-model-title">Classificador específico</h3>
              </div>
              <p className="lp-model-desc">
                Encoder visual ViT pré-treinado pela Meta com aprendizado auto-supervisionado
                em 142 milhões de imagens. Extrai vetores de features de alta dimensão que
                capturam estrutura visual fina, ideal para morfologia de insetos.
              </p>
              <ul className="lp-model-facts">
                <li><Check /> Treinado nas espécies do gênero <em>Augochloropsis</em></li>
                <li><Check /> Acurácia top-1 acima de 90% nos testes</li>
                <li><Check /> Resultado em menos de 3 segundos</li>
                <li><Check /> Score de confiança por classe para auditoria</li>
              </ul>
            </div>

            {/* CLIP */}
            <div className="lp-model-card lp-model-card-amber">
              <div className="lp-model-header">
                <span className="lp-model-badge lp-model-badge-amber">CLIP (OpenAI)</span>
                <h3 className="lp-model-title">Identificação geral</h3>
              </div>
              <p className="lp-model-desc">
                Modelo multimodal da OpenAI treinado em 400 milhões de pares imagem-texto.
                Realiza identificação zero-shot sem necessidade de treinamento adicional,
                cobrindo espécies além do gênero <em>Augochloropsis</em>.
              </p>
              <ul className="lp-model-facts">
                <li><Check /> Identificação zero-shot sem fine-tuning</li>
                <li><Check /> Cobre 5 espécies de abelhas e vespas</li>
                <li><Check /> Não requer imagens de treinamento</li>
                <li><Check /> Probabilidade por espécie via similaridade textual</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ── Species ─────────────────────────────────────────────────────────── */}
      <section className="lp-section lp-section-alt" id="species" aria-labelledby="species-title">
        <HoneycombBg opacity={0.04} />
        <div className="lp-section-inner">
          <div className="lp-reveal">
            <div className="lp-eyebrow lp-eyebrow-green">Espécies</div>
            <h2 id="species-title" className="lp-section-title">O que o sistema identifica</h2>
            <p className="lp-section-sub">
              Sete espécies distribuídas entre dois modelos. Novas espécies podem ser
              adicionadas ao classificador específico com novos dados de treinamento.
            </p>
          </div>

          <div className="lp-species-groups lp-stagger">
            {SPECIES_GROUPS.map((group) => (
              <div key={group.model} className="lp-species-group">
                <div className="lp-species-group-header">
                  <span
                    className="lp-species-model-tag"
                    style={{ borderColor: group.color, color: group.color }}
                  >
                    {group.model}
                  </span>
                  <div>
                    <div className="lp-species-group-title">{group.label}</div>
                    <div className="lp-species-group-sub">{group.sublabel}</div>
                  </div>
                </div>

                <div className="lp-species-list">
                  {group.species.map((sp) => (
                    <div key={sp.sci} className="lp-species-item" style={{ '--sp-color': group.color } as React.CSSProperties}>
                      <span className="lp-species-sci">{sp.sci}</span>
                      <span className="lp-species-common">{sp.common}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ────────────────────────────────────────────────────── */}
      <section className="lp-section" id="how-it-works" aria-labelledby="pipeline-title">
        <HoneycombBg opacity={0.04} />
        <div className="lp-section-inner lp-section-inner-centered">
          <div className="lp-reveal">
            <div className="lp-eyebrow lp-eyebrow-green">Pipeline</div>
            <h2 id="pipeline-title" className="lp-section-title">Como funciona</h2>
            <p className="lp-section-sub">
              Cinco etapas desde o upload até a classificação final com score de confiança.
            </p>
          </div>

          <div className="lp-pipeline-grid lp-reveal">
            {[
              {
                step: '01', title: 'Upload da imagem', color: '#2C4A6E',
                desc: 'Foto da abelha enviada via interface web. A imagem trafega à API via multipart/form-data.',
              },
              {
                step: '02', title: 'Pré-processamento', color: '#2C4A6E',
                desc: 'Redimensionamento para 224×224 px, normalização com estatísticas ImageNet e conversão para tensor.',
              },
              {
                step: '03', title: 'Extração de embeddings', color: '#4A7C59',
                desc: 'DINOv2 (ViT) extrai um vetor de features de alta dimensão capturando a estrutura visual da abelha.',
              },
              {
                step: '04', title: 'Classificação', color: '#B8860B',
                desc: 'Um MLP treinado nos embeddings mapeia o vetor para probabilidades por espécie via softmax.',
              },
              {
                step: '05', title: 'Resultado com confiança', color: '#B8860B',
                desc: 'Retorna a espécie predita, o score de confiança e as probabilidades de todas as classes.',
              },
            ].map((item) => (
              <div key={item.step} className="lp-pipeline-card">
                <div
                  className="lp-pipeline-card-circle"
                  style={{ borderColor: item.color, color: item.color }}
                >
                  {item.step}
                </div>
                <div className="lp-pipeline-card-step" style={{ color: item.color }}>
                  Etapa {item.step}
                </div>
                <h3 className="lp-pipeline-card-title">{item.title}</h3>
                <p className="lp-pipeline-card-desc">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Academic / Team ─────────────────────────────────────────────────── */}
      <section className="lp-section lp-section-alt" id="team" aria-labelledby="team-title">
        <HoneycombBg opacity={0.05} />
        <div className="lp-section-inner">
          <div className="lp-reveal">
            <div className="lp-eyebrow lp-eyebrow-green">Contexto Acadêmico</div>
            <h2 id="team-title" className="lp-section-title">Projeto Integrador de IA</h2>
          </div>

          <div className="lp-team-grid lp-stagger">
            {[
              {
                Icon: IconDiploma,
                title: 'Objetivo acadêmico',
                accent: 'lp-card-green',
                desc: 'Aplicar técnicas de visão computacional e aprendizado de máquina a um problema real de taxonomia de insetos, integrando biologia, engenharia de software e IA.',
              },
              {
                Icon: IconNetwork,
                title: 'Parceria com pesquisa',
                accent: 'lp-card-amber',
                desc: 'Desenvolvido com pesquisadores de entomologia para validar a metodologia e construir um dataset representativo de espécies do gênero Augochloropsis.',
              },
              {
                Icon: IconBarChart,
                title: 'Impacto esperado',
                accent: 'lp-card-green',
                desc: 'Reduzir o tempo de classificação de minutos para segundos, democratizar o acesso à identificação taxonômica e gerar dados em escala para biodiversidade.',
              },
            ].map((item) => (
              <div key={item.title} className={`lp-card ${item.accent}`}>
                <span className="lp-card-icon-wrap"><item.Icon /></span>
                <h3 className="lp-card-title">{item.title}</h3>
                <p className="lp-card-desc">{item.desc}</p>
              </div>
            ))}
          </div>

          {/* Final CTA */}
          <div className="lp-cta-block lp-reveal">
            <HoneycombBg opacity={0.07} />
            <div style={{ position: 'relative' }}>
              <h3 className="lp-cta-title">Pronto para classificar sua amostra?</h3>
              <p className="lp-cta-sub">
                Faça upload de uma imagem e obtenha a identificação da espécie em segundos.
              </p>
              <Link to="/app" className="lp-btn-primary" style={{ display: 'inline-flex' }}>
                Acessar o sistema <ArrowRight />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────────────── */}
      <footer className="lp-footer">
        <div className="lp-footer-inner">
          <div className="lp-footer-brand">
            <img src="/logosolucoesmobile.png" alt="BeeAI" className="lp-footer-logo" />
            <span className="lp-footer-brand-name">BeeAI</span>
            <span>— Identificação inteligente de espécies</span>
          </div>
          <span className="lp-footer-tech">
            PyTorch · DINOv2 · CLIP · FastAPI · React · PostgreSQL · Docker
          </span>
        </div>
      </footer>
    </div>
  )
}
