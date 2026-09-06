document.addEventListener('DOMContentLoaded', function () {
  // Mobile navigation
  const menu = document.querySelector('.menu');
  const links = document.querySelector('.links');

  if (menu && links) {
    menu.addEventListener('click', function () {
      const open = links.classList.toggle('open');
      menu.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    links.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        links.classList.remove('open');
        menu.setAttribute('aria-expanded', 'false');
      });
    });
  }

  const grid = document.getElementById('posts');
  const filters = Array.from(document.querySelectorAll('.filter'));
  const search = document.getElementById('search');
  const clear = document.getElementById('clearSearch');
  const sort = document.getElementById('sort');
  const count = document.getElementById('resultCount');
  const empty = document.getElementById('empty');
  const pagination = document.getElementById('pagination');
  const cards = Array.from(document.querySelectorAll('.card'));

  const state = { filter: 'all', query: '', sort: 'newest', page: 1, perPage: 6 };
  const otherCategories = ['hackthebox', 'portswigger', 'wifi', 'tryhackme', 'vulnlab'];

  function matches(card) {
    const category = (card.dataset.cat || 'other').toLowerCase();
    const haystack = [
      card.dataset.title || '',
      card.dataset.search || '',
      card.textContent || ''
    ].join(' ').toLowerCase();

    const categoryOK =
      state.filter === 'all' ||
      category === state.filter ||
      (state.filter === 'other' && !otherCategories.includes(category));

    return categoryOK && (!state.query || haystack.includes(state.query));
  }

  function sortCards(list) {
    return list.slice().sort(function (a, b) {
      const ad = a.dataset.date || '';
      const bd = b.dataset.date || '';
      const at = (a.dataset.title || '').toLowerCase();
      const bt = (b.dataset.title || '').toLowerCase();

      if (state.sort === 'oldest') return ad.localeCompare(bd);
      if (state.sort === 'az') return at.localeCompare(bt, 'es');
      if (state.sort === 'za') return bt.localeCompare(at, 'es');

      return bd.localeCompare(ad);
    });
  }

  function makePageButton(label, page, active, disabled) {
    const button = document.createElement('button');

    button.type = 'button';
    button.className = 'page-btn' + (active ? ' active' : '');
    button.textContent = label;
    button.disabled = !!disabled;

    if (active) {
      button.setAttribute('aria-current', 'page');
    }

    button.addEventListener('click', function () {
      if (button.disabled || page === state.page) return;

      state.page = page;
      render();

      const section = document.getElementById('writeups');

      if (section) {
        section.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });

    return button;
  }

  function renderPagination(totalPages) {
    if (!pagination) return;

    pagination.replaceChildren();

    if (totalPages <= 1) return;

    pagination.appendChild(
      makePageButton(
        '‹',
        state.page - 1,
        false,
        state.page === 1
      )
    );

    const pages = [];

    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else if (state.page <= 4) {
      pages.push(1, 2, 3, 4, 5, 'dots', totalPages);
    } else if (state.page >= totalPages - 3) {
      pages.push(
        1,
        'dots',
        totalPages - 4,
        totalPages - 3,
        totalPages - 2,
        totalPages - 1,
        totalPages
      );
    } else {
      pages.push(
        1,
        'dots',
        state.page - 1,
        state.page,
        state.page + 1,
        'dots',
        totalPages
      );
    }

    pages.forEach(function (item) {
      if (item === 'dots') {
        const span = document.createElement('span');

        span.className = 'dots';
        span.textContent = '…';

        pagination.appendChild(span);
      } else {
        pagination.appendChild(
          makePageButton(
            String(item),
            item,
            item === state.page,
            false
          )
        );
      }
    });

    pagination.appendChild(
      makePageButton(
        '›',
        state.page + 1,
        false,
        state.page === totalPages
      )
    );
  }

  function render() {
    const matching = sortCards(cards.filter(matches));
    const total = matching.length;
    const totalPages = Math.max(
      1,
      Math.ceil(total / state.perPage)
    );

    if (state.page > totalPages) {
      state.page = totalPages;
    }

    const start = (state.page - 1) * state.perPage;
    const visible = matching.slice(
      start,
      start + state.perPage
    );

    const visibleSet = new Set(visible);

    // Restore the original DOM order, then hide everything not on this page.
    cards.forEach(function (card) {
      card.hidden = !visibleSet.has(card);
      card.style.display = visibleSet.has(card) ? '' : 'none';
      grid.appendChild(card);
    });

    // Put current-page cards at the front in the requested sort order.
    visible
      .slice()
      .reverse()
      .forEach(function (card) {
        grid.prepend(card);
      });

    if (count) {
      const shown = Math.min(
        state.perPage,
        Math.max(0, total - start)
      );

      count.textContent = total
        ? 'Mostrando ' + shown + ' de ' + total + ' writeups'
        : 'Mostrando 0 writeups';
    }

    if (empty) {
      empty.hidden = total !== 0;
    }

    renderPagination(totalPages);
  }

  filters.forEach(function (button) {
    button.addEventListener('click', function () {
      filters.forEach(function (b) {
        b.classList.remove('active');
      });

      button.classList.add('active');

      state.filter = button.dataset.filter || 'all';
      state.page = 1;

      render();
    });
  });

  if (search) {
    search.addEventListener('input', function () {
      state.query = search.value.trim().toLowerCase();
      state.page = 1;

      if (clear) {
        clear.style.visibility = state.query
          ? 'visible'
          : 'hidden';
      }

      render();
    });
  }

  if (clear) {
    clear.addEventListener('click', function () {
      if (!search) return;

      search.value = '';
      state.query = '';
      state.page = 1;

      clear.style.visibility = 'hidden';

      search.focus();

      render();
    });
  }

  if (sort) {
    sort.addEventListener('change', function () {
      state.sort = sort.value;
      state.page = 1;

      render();
    });
  }

  document.querySelectorAll('.copy-code').forEach(function (button) {
    button.addEventListener('click', async function () {
      const code = button
        .closest('.code-window')
        ?.querySelector('code');

      if (!code) return;

      try {
        await navigator.clipboard.writeText(code.textContent);

        const old = button.textContent;
        button.textContent = 'Copied!';

        setTimeout(function () {
          button.textContent = old;
        }, 1400);
      } catch (_) {}
    });
  });

  document.querySelectorAll('[data-copy-url]').forEach(function (button) {
    button.addEventListener('click', async function () {
      try {
        await navigator.clipboard.writeText(location.href);
      } catch (_) {}

      const old = button.textContent;
      button.textContent = '✓';

      setTimeout(function () {
        button.textContent = old;
      }, 1400);
    });
  });

  if (clear) {
    clear.style.visibility = 'hidden';
  }

  render();
});
