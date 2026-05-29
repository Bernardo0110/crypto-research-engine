# Guia de Triagem — Sessão de Melhorias

Este documento define como triar o output do Gemini durante uma sessão de melhorias.
Leia antes de classificar qualquer item da avaliação.

---

## Filtro de Impacto Global (aplicar antes de classificar)

Antes de atribuir um bucket a qualquer item, responder mentalmente:

> *"Esta alteração toca um contrato de função, reorganiza módulos, cria dependência nova ou muda comportamento em mais de um lugar do pipeline?"*

- **Sim** → não implementar autonomamente, independentemente do bucket. Registrar na seção "Alterações escaladas" do relatório final para o usuário avaliar.
- **Não** → seguir para classificação normal abaixo.

O objetivo é manter o projeto coerente e organizado. Uma correção isolada que introduz padrão inconsistente ou complexidade desnecessária é pior do que deixar o bug no lugar.

---

## Os 4 Buckets

### Bucket A — Erro real
**O que é:** bug de lógica, cálculo incorreto, dado exibido de forma enganosa, inconsistência entre seções do PDF.
**Exemplos:**
- Score calculado com peso errado
- Gráfico mostrando escala ou unidade incorreta
- FDV/MCap calculado invertido
- Número na capa diverge do número no apêndice
- Fórmula descrita na metodologia difere da implementação

**Ação:** implementar nesta rodada, sem exceção.

---

### Bucket B — Artefato de dado
**O que é:** número que parece errado mas é correto dado as limitações das fontes (CoinGecko, DeFiLlama, Blockchain.info, Etherscan, OKX).
**Exemplos:**
- Métricas on-chain ausentes → coin não é BTC nem ETH (suporte limitado por design)
- Protocol Revenue como N/D → coin não é DeFi (esperado)
- Developer score baixo → repositório privado ou projeto sem GitHub público
- Hash rate ausente para altcoins → apenas BTC/ETH têm suporte
- Google Trends em 0 → coin muito nichado para ter dados de busca suficientes
- Funding rate ausente → coin sem mercado perp na OKX

**Ação:** documentar como limitação conhecida. Não alterar código. Se o Gemini insistir, adicionar nota explicativa no PDF.

---

### Bucket C — Melhoria de UX / visual / narrativa
**O que é:** algo que funciona mas pode ser mais claro, legível ou profissional.
**Exemplos:**
- Label de eixo ausente ou ambíguo
- Texto repetitivo entre seções
- Ordem de informações poderia ser mais lógica
- Cor ou tamanho de fonte subótimos
- Unidade monetária ambígua (USD vs BTC)

**Critério de aprovação:** custo de implementação estimado em menos de 30 minutos.
**Ação:** implementar se aprovado. Descartar se o esforço for desproporcional ao ganho.

---

### Bucket D — Feature nova
**O que é:** módulo, seção ou funcionalidade que ainda não existe no projeto.

**Subdivisão obrigatória:**

| Sub-bucket | Critério | Ação |
|------------|----------|------|
| D-fácil | Viável com as fontes atuais (CoinGecko, DeFiLlama, GitHub, OKX, Blockchain.info), implementável em menos de 2h | Implementar nesta rodada |
| D-profundo | Requer nova fonte de dados, integração externa paga, ou mudança arquitetural significativa | Adicionar ao backlog com prioridade |

---

## Checklist de triagem (fazer antes de implementar)

- [ ] Apliquei o Filtro de Impacto Global em cada item antes de classificar
- [ ] Reli todos os itens da avaliação pelo menos uma vez antes de classificar
- [ ] Separei os B dos A (não confundir dado ausente por limitação de fonte com bug de código)
- [ ] Avaliei o custo real de cada C antes de aprovar
- [ ] Para cada D, verifiquei se as fontes de dados já disponíveis suportam a feature
- [ ] Verifiquei se o prompt `avaliar_relatorio.md` precisa de ajuste para a próxima rodada

---

## Critério de parada do loop

Encerrar a sessão quando **todas** as condições abaixo forem verdadeiras:
- Nenhum item Bucket A identificado na última avaliação
- Menos de 3 itens acionáveis (A + C aprovados + D-fácil) na última rodada
- Backlog atualizado com os D-profundos da sessão

---

## Ao final de cada sessão

Apresentar ao usuário:
1. Resumo das rodadas: quantas foram, o que mudou em cada uma
2. Lista de B documentados (limitações conhecidas das fontes crypto)
3. Backlog atualizado (`outputs/backlog_melhorias.md`)
4. Sugestão de ajuste ao prompt de avaliação, se identificado
