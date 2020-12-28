var host = 'http://' + window.location.host;
var parser = new DOMParser()
var currentPage = 0;

function renderPostItem(link) {
  li = document.createElement('li')
  src = document.createElement('a')
  src.setAttribute('href', link['path'])
  src.setAttribute('target', '_blank')
  src.innerText = `[${link['source']}] `
  li.appendChild(src)
  a = document.createElement('a')
  a.setAttribute('href', './posts/' + link['slug'])
  a.setAttribute('target', '_blank')
  a.innerText = link['title'];
  li.appendChild(a)
  dt = document.createElement('span')
  dt.innerText = link['date']
  dt.setAttribute('class', 'date')
  li.appendChild(dt)
  document.getElementById('post_link_container').appendChild(li)
}

function loadMore(limit) {
  fetch(host + '/api/post_links' + `?page=${currentPage}&pageSize=${limit}`).then(resp => {
    resp.json().then(data => {
      for (item of data) {
        renderPostItem(item);
      }
      currentPage += 1;
    });
  });
}
