const search = document.querySelector('#electorate-search');
if (search) {
  const rows = [...document.querySelectorAll('[data-search-key]')];
  document.querySelector('.electorate-search').hidden = false;
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('en-NZ').replace(/\s+/g, ' ').trim();
  search.addEventListener('input', () => {
    const query = normalize(search.value);
    for (const row of rows) row.hidden = !row.dataset.searchKey.includes(query);
    document.querySelector('#search-result').textContent = `${rows.filter(row => !row.hidden).length} electorates found`;
  });
}
