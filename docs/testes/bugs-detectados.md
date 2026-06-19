# Mapeamento de Bugs por Teste — US01 e US02

Este documento lista, para cada teste automatizado, **qual bug específico ele detectaria** se o código estivesse com defeito. O objetivo é mostrar que os testes não foram escritos por acidente — cada um existe porque um bug real e plausível poderia acontecer naquele ponto.

Os testes estão divididos em duas suítes:
- **Backend** (`pytest` + Flask test client): valida regras de negócio diretamente nas rotas e services, sem browser.
- **UI** (`pytest` + Playwright): valida a interface real no Railway, com browser Chromium, em dois viewports.

---

## Suíte 1 — Backend (`backend/tests/`)

### US01 — Admin cadastra usuários (`test_us01_cadastro_usuarios.py`)

| Teste | Bug que detecta |
|---|---|
| `test_cadastro_aluno_retorna_status_pendente` | Usuário criado diretamente como ATIVO, sem precisar trocar a senha — violação da regra de primeiro acesso. |
| `test_cadastro_professor_retorna_status_pendente` | Mesma vulnerabilidade acima aplicada ao papel PROFESSOR. |
| `test_cadastro_exibe_senha_temporaria` | Senha temporária gerada mas não exibida ao admin — ele não tem como informar o usuário, que fica bloqueado. |
| `test_email_duplicado_rejeitado` | Sistema permite duas contas com o mesmo email — login passa a ser ambíguo e dados de usuários distintos podem se misturar. |
| `test_email_duplicado_case_insensitive` | `"BOB@TESTE.COM"` e `"bob@teste.com"` são aceitos como emails diferentes, criando conta duplicada porque a normalização para minúsculas não foi aplicada. |
| `test_sem_nome_rejeitado` | Usuário criado sem nome — campo fica vazio no sistema e na interface, sem como identificar a pessoa. |
| `test_sem_email_rejeitado` | Usuário criado sem email — não consegue fazer login, nem receber comunicações. |
| `test_sem_papel_rejeitado` | Usuário criado sem papel definido — o sistema não sabe o que exibir nem quais permissões aplicar. |

---

### US02 — Login (`test_us02_login.py`)

| Teste | Bug que detecta |
|---|---|
| `test_admin_redireciona_para_usuarios` | Após login, admin é mandado para a home genérica em vez do painel de usuários — perde a navegação esperada para o seu papel. |
| `test_aluno_redireciona_para_home` | Aluno é redirecionado para uma rota que não existe ou não tem permissão — tela de erro logo após o login. |
| `test_professor_redireciona_para_home` | Mesmo problema para o papel professor. |
| `test_login_cria_sessao_com_dados_do_usuario` | Sessão criada sem `user_id` ou `papel` — todas as páginas autenticadas ficam quebradas (o decorator `login_required` nega acesso a tudo). |
| `test_senha_errada_exibe_erro_generico` | Mensagem de erro diferente para "senha errada" vs "email não existe" — revela ao atacante se um email está cadastrado no sistema (enumeração de usuários). |
| `test_email_inexistente_exibe_mesmo_erro_generico` | Complemento do anterior: garante que ambos os casos retornam a mesma mensagem, bloqueando a enumeração. |
| `test_credenciais_invalidas_nao_criam_sessao` | **Crítico:** login com credenciais erradas ainda cria uma sessão válida — qualquer pessoa acessa o sistema sem autenticação real. |
| `test_usuario_pendente_redireciona_primeiro_acesso` | Usuário PENDENTE bypassa o fluxo de primeiro acesso e entra direto no sistema com senha temporária, sem nunca ter definido uma senha própria. |
| `test_usuario_pendente_armazena_id_na_sessao` | Estado de primeiro acesso não é salvo na sessão — ao abrir a tela de troca de senha, o sistema não sabe para qual usuário a nova senha deve ser salva. |
| `test_usuario_inativo_login_negado` | Usuário desativado pelo admin consegue fazer login normalmente — a desativação não tem efeito real. |
| `test_usuario_inativo_nao_cria_sessao` | **Crítico:** mesmo com login negado por conta inativa, uma sessão é criada no servidor — o usuário pode acessar rotas autenticadas diretamente pela URL. |

---

## Suíte 2 — UI (`backend/tests/ui/`)

Os testes de UI detectam uma categoria diferente de bugs: **problemas que existem na camada visual e de interação**, invisíveis para os testes de backend. O backend pode estar correto e mesmo assim a interface estar quebrada.

---

### US01 — Cadastro de Usuários via Interface

#### Desktop (`TestUS01CadastroDesktop`)

| Teste | Bug que detecta |
|---|---|
| `test_botao_novo_usuario_visivel` | Botão "Novo usuário" existe no HTML mas está oculto por CSS (`display: none`, `visibility: hidden` ou fora do viewport) — admin não consegue abrir o formulário. |
| `test_dialog_abre_ao_clicar_novo_usuario` | Clique no botão não abre o `<dialog>` — erro de JavaScript, ID errado no `onclick`, ou elemento `<dialog>` ausente do DOM. |
| `test_dialog_tem_campos_nome_email_e_papel` | Um dos campos (`nome`, `email` ou `papel`) foi removido acidentalmente do template do dialog — admin não consegue preencher o formulário. |
| `test_cadastro_exibe_senha_temporaria_no_toast` | Toast de senha temporária não aparece na tela após o cadastro — admin vê uma tela em branco sem saber qual senha foi gerada, não tem como informar o novo usuário. |
| `test_usuario_aparece_na_lista_com_status_pendente` | Usuário é criado no banco mas a lista não atualiza (bug de redirect), ou o badge de status "Pendente" está faltando no template. |
| `test_email_duplicado_exibe_flash_de_erro` | Flash de erro (`"Email já cadastrado"`) é gerado pelo backend mas não renderizado no template — admin vê uma página em branco sem feedback do erro. |
| `test_campo_nome_required_impede_submissao` | Atributo `required` foi removido do campo `nome` — formulário é submetido vazio, e o erro só aparece depois do POST (pior UX e request desnecessário). |
| `test_campo_email_required_impede_submissao` | Mesma regressão para o campo `email`. |
| `test_campo_papel_required_impede_submissao` | Mesma regressão para o `<select>` de papel — formulário submetido sem papel selecionado. |

#### Mobile (`TestUS01CadastroMobile`)

| Teste | Bug que detecta |
|---|---|
| `test_botao_novo_usuario_visivel_no_mobile` | Botão "Novo usuário" existe no desktop mas some no mobile — CSS responsivo com `display: none` ou overflow incorreto. |
| `test_dialog_abre_no_mobile` | `<dialog>` não abre no viewport mobile — problema de z-index, posicionamento fixo que sai do viewport ou toque não registrado. |
| `test_cadastro_completo_funciona_no_mobile` | Form dentro do dialog não é submetível no mobile — campos fora do scroll, botão de submit coberto por teclado virtual ou evento de toque não disparado. |
| `test_email_duplicado_exibe_erro_no_mobile` | Mensagem de erro visível no desktop mas cortada ou fora do viewport no mobile devido a layout fixo. |

---

### US02 — Login via Interface

#### Desktop (`TestUS02LoginDesktop`)

| Teste | Bug que detecta |
|---|---|
| `test_formulario_login_tem_campos_corretos` | Campo de email ou senha com atributo `name` errado — form submetido sem o valor do campo, backend recebe string vazia e rejeita sem mensagem clara. |
| `test_admin_login_exibe_sidebar_e_redireciona` | Sidebar não renderiza após login — CSS de `.app-shell` quebrado, sessão não injetada no `context_processor`, ou template `base.html` não carregado. |
| `test_senha_errada_exibe_alerta_na_tela` | Flash de erro existe no backend mas não é renderizado no `base_auth.html` — tela de login fica em branco após erro, usuário não sabe o que aconteceu. |
| `test_email_inexistente_exibe_mesmo_alerta` | Mensagem de erro diferente para email inexistente vs senha errada — revela ao atacante se o email está cadastrado (mesmo bug de segurança, mas verificado pela UI). |
| `test_erro_nao_redireciona_permanece_no_login` | Após credenciais erradas, usuário é redirecionado para outra página em vez de permanecer no login — bug de redirect incorreto na rota. |
| `test_fluxo_completo_primeiro_acesso` | **Fluxo end-to-end:** qualquer quebra no caminho admin cria usuário → senha aparece na tela → logout → login com senha temp → redirecionamento para primeiro acesso. Detecta: toast sem senha, sessão de primeiro acesso não criada, redirect errado. |
| `test_fluxo_completo_usuario_inativo` | **Fluxo end-to-end com dialog:** qualquer quebra em desativar usuário via `<dialog>` nativo → confirmar → logout → login negado. Detecta: dialog não abrindo, desativação não persistida no banco, mensagem de conta inativa não exibida. |

#### Mobile (`TestUS02LoginMobile`)

| Teste | Bug que detecta |
|---|---|
| `test_formulario_login_visivel_e_usavel_no_mobile` | Campos de login somem ou ficam inacessíveis no mobile — CSS com largura fixa que extrapola o viewport, ou `overflow: hidden` no container. |
| `test_login_bem_sucedido_no_mobile` | Login funciona no desktop mas não no mobile — problema de cookies de sessão com viewport ou user-agent de mobile simulado. |
| `test_alerta_erro_visivel_no_mobile` | Mensagem de erro aparece no HTML mas está fora da área visível no mobile — container com altura fixa que corta o alerta. |

---

## Por que dois tipos de teste?

| | Backend (`pytest`) | UI (`Playwright`) |
|---|---|---|
| **O que testa** | Regras de negócio, validações, sessão, banco | Interface visual, interação, responsividade |
| **Velocidade** | ~30 segundos | ~2 minutos |
| **Ambiente** | Banco local isolado (`monitoria_test`) | Railway (ambiente real) |
| **Bugs que pega** | Lógica errada, dados incorretos, segurança | CSS quebrado, JS com erro, dialog não abrindo, mobile com layout ruim |
| **Bugs que não pega** | CSS, JS, responsividade | Validações internas de banco, regras de negócio isoladas |

Juntos, os 42 testes cobrem tanto a camada de negócio quanto a camada visual, garantindo que o sistema funciona de ponta a ponta.
