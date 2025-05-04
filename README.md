Gerador de Provas Escolares
O Gerador de Provas Escolares é uma aplicação web desenvolvida com Streamlit e Python, projetada para auxiliar professores na criação de provas escolares de forma simples e eficiente. Com esse sistema, é possível adicionar questões dissertativas ou de múltipla escolha, incluir imagens nas questões, editar e excluir questões, além de exportar a prova final em formato Word (.docx), pronta para ser impressa ou distribuída aos alunos.

Funcionalidades
Cadastro de Informações
O usuário pode preencher as informações principais da prova, como o nome do professor, a disciplina, a série/turma, o bimestre e a data da prova.

O sistema permite o upload de um logo da escola, que pode ser incluído no cabeçalho da prova.

Criação de Questões
O usuário pode adicionar questões de dois tipos: Dissertativas e Múltipla Escolha.

Para questões de múltipla escolha, é possível adicionar até 4 opções de resposta (A, B, C, D).

As questões também podem incluir imagens, facilitando a utilização de gráficos ou ilustrações.

Edição e Exclusão de Questões
As questões adicionadas podem ser editadas ou excluídas diretamente na interface, permitindo um gerenciamento fácil e rápido.

Exportação para Word
A prova gerada pode ser exportada para um arquivo Word (.docx), que incluirá todas as questões e configurações definidas.

O sistema permite a inclusão do logo da escola no cabeçalho da prova.

Como Usar
Pré-requisitos
Python 3.8 ou superior.

Instalar as dependências do projeto com o comando:

bash
Copiar
Editar
pip install -r requirements.txt
Executando a Aplicação
Para rodar a aplicação localmente, basta executar o seguinte comando:

bash
Copiar
Editar
streamlit run app.py
Isso iniciará o servidor local e você poderá acessar a aplicação em [http://localhost:8501](https://geradordeprovasapp-vfeg5aytkrrk5akmp8wwxc.streamlit.app).

Passo a Passo para Criar a Prova
Configuração Inicial:

No lado esquerdo da tela, você pode adicionar o logo da escola e preencher as informações gerais da prova: nome do professor, disciplina, série/turma, bimestre e data.

Adicionar Questões:

Escolha o tipo da questão (dissertativa ou múltipla escolha).

Adicione o texto da questão e, caso queira, faça o upload de uma imagem relacionada à questão.

Para questões de múltipla escolha, insira as opções A, B, C e D.

Edição e Exclusão:

Após adicionar as questões, você pode editar ou excluir qualquer uma delas. Ao clicar nas opções de editar, os campos se preenchem novamente com os dados da questão selecionada para que você possa realizar alterações.

Gerar Prova:

Após adicionar todas as questões, clique no botão "💾 Gerar Documento Word".

O sistema gerará o arquivo .docx com as questões e todos os detalhes configurados, que pode ser baixado e impresso.

Tecnologias Usadas
Streamlit: Framework Python utilizado para criar a interface web interativa.

Python-docx: Biblioteca para criação e manipulação de arquivos do Microsoft Word.

Pillow: Biblioteca para manipulação de imagens.

Datetime: Para manipulação de datas (como a data da prova).

Como Contribuir
Faça um fork do projeto.

Crie uma nova branch (git checkout -b minha-nova-feature).

Realize as alterações e commit.

Envie um pull request para o repositório principal.

Licença
Este projeto está licenciado sob a Licença MIT.
