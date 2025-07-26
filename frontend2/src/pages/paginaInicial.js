import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

export default function PaginaInicial() {
  const [produtosFiltrados, setProdutosFiltrados] = useState([]);
  const [filtro, setFiltro] = useState('');
  const [categorias, setCategorias] = useState([]);
  const [categoriaSelecionada, setCategoriaSelecionada] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/tipos')
      .then(res => res.json())
      .then(data => setCategorias(data))
      .catch(err => console.error('Erro ao buscar categorias:', err));
  }, []);

  useEffect(() => {
    let url = 'http://localhost:5000/pratos';

    const termo = filtro.trim();
    if (termo) {
      url = `http://localhost:5000/pratos/buscar?q=${encodeURIComponent(termo)}`;
    } else if (categoriaSelecionada) {
      url = `http://localhost:5000/pratos/tipo/${categoriaSelecionada}`;
    }

    fetch(url)
      .then(res => res.json())
      .then(data => setProdutosFiltrados(data))
      .catch(err => {
        console.error('Erro ao buscar produtos:', err);
        setProdutosFiltrados([]);
      });
  }, [filtro, categoriaSelecionada]);

  function irParaPerfil() {
    navigate('/perfil');
  }

  function abrirDetalhes(id) {
    navigate(`/pratos/${id}`);
  }

  function irParaAdicionarProduto() {
    navigate('/adicionar-produto');
  }

  function irParaCarrinho() {
    navigate('/carrinho');
  }

  function adicionarAoCarrinho(e, pratoId) {
    e.stopPropagation();
    fetch('http://localhost:5000/pedido', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prato_id: pratoId }),
    })
      .then(res => res.json())
      .then(data => alert(data.mensagem || data.erro))
      .catch(() => alert('Erro ao adicionar ao carrinho'));
  }

  return (
    <div className="pagina-inicial">
      <header className="header">
        <h1>Feed de Pratos</h1>
        <div className="botoes-topo">
          <button className="botao-perfil" onClick={irParaPerfil}>Ver Perfil</button>
          <button className="botao-adicionar" onClick={irParaAdicionarProduto}>Adicionar Produto</button>
          <button
            className="botao-carrinho topo"
            onClick={irParaCarrinho}
            aria-label="Ver carrinho"
            title="Ver pedidos"
          >
<svg
  className="icone-carrinho"
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 64 64"
  width="24"
  height="24"
  fill="currentColor"
>
  <path d="M4 36c0 11.05 8.95 20 20 20h16c11.05 0 20-8.95 20-20H4z" />
  <path d="M20 4s2 4 0 8 2 8 2 8M32 4s2 4 0 8 2 8 2 8M44 4s2 4 0 8 2 8 2 8" stroke="currentColor" strokeWidth="2" fill="none"/>
</svg>

          </button>
        </div>
      </header>

      {/* Barra de busca com classe */}
      <div className="filtros-container">
      <input
        type="text"
        placeholder="Buscar pratos pelo nome..."
        value={filtro}
        onChange={e => {
          setFiltro(e.target.value);
          setCategoriaSelecionada('');
        }}
        className="barra-pesquisa"
      />

      {/* Filtro de categoria com classe */}
      <select
        value={categoriaSelecionada}
        onChange={e => {
          setCategoriaSelecionada(e.target.value);
          setFiltro('');
        }}
        className="select-categoria"
      >
        <option value="">Filtrar por tipo...</option>
        {categorias.map(c => (
          <option key={c.id} value={c.id}>{c.nome}</option>
        ))}
      </select>
      </div>

      <div className="lista-produtos">
        {produtosFiltrados.length === 0 ? (
          <p>Nenhum prato encontrado.</p>
        ) : (
          produtosFiltrados.map(produto => (
            <div
              key={produto.id}
              className="card-produto"
              onClick={() => abrirDetalhes(produto.id)}
            >
              <img
                src={produto.imagem_url}
                alt={produto.nome}
                className="imagem-produto"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = '/img/imagem-nao-disponivel.png';
                }}
              />
              <h3>{produto.nome}</h3>
              <p>Preço: R$ {produto.preco.toFixed(2)}</p>
              <button
                className="botao-carrinho card"
                onClick={(e) => adicionarAoCarrinho(e, produto.id)}
                aria-label={`Adicionar ${produto.nome} ao carrinho`}
                title="Adicionar aos pedidos"
              >
<svg
  className="icone-carrinho"
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 64 64"
  width="24"
  height="24"
  fill="currentColor"
>
  <path d="M4 36c0 11.05 8.95 20 20 20h16c11.05 0 20-8.95 20-20H4z" />
  <path d="M20 4s2 4 0 8 2 8 2 8M32 4s2 4 0 8 2 8 2 8M44 4s2 4 0 8 2 8 2 8" stroke="currentColor" strokeWidth="2" fill="none"/>
</svg>

              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
