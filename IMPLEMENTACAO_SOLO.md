# Implementação da Taxonomia SOLO

Esta versão introduz a Taxonomia SOLO como camada pedagógica intermédia antes da geração multimédia.

## Alterações principais

1. O `PedagogicalDesigner` gera agora resultados de aprendizagem estruturados em `solo_learning_outcomes`.
2. Cada resultado inclui:
   - `id`
   - `outcome_type`
   - `solo_level`
   - `action_verb`
   - `description`
   - `importance`
   - `related_topics`
   - `suggested_learning_activity`
   - `suggested_assessment`
3. O nível `SOLO_1` não é usado para resultados de aprendizagem.
4. Cada slide da `slide_sequence` é ligado a um ou mais resultados através de `learning_outcome_ids`.
5. O `MultimediaGenerator` consome os resultados SOLO para enriquecer notas, descrições visuais, prompts de imagem e plano de slides.
6. A interface Gradio tem um novo separador `SOLO` para rever os resultados antes da aprovação da estrutura.
7. O PowerPoint inclui uma etiqueta por slide com o nível SOLO e os resultados de aprendizagem associados.

## Fluxo atualizado

```text
Requisitos
  -> Análise conceptual
  -> Resultados de aprendizagem SOLO + Estrutura pedagógica
  -> Validação humana
  -> Plano multimédia / slides
  -> Exportação PowerPoint
```

## Como usar no chat

Depois de rever o separador SOLO e a estrutura, pode escrever, por exemplo:

- `Aprovo os resultados e a estrutura.`
- `Reformula os resultados SOLO e torna-os mais práticos.`
- `Os resultados estão demasiado avançados para este público, baixa o nível SOLO.`

