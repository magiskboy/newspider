var host = 'http://' + window.location.host;
var parser = new DOMParser()
var currentOffset = 10;

function renderPostItem(link) {
  a = document.createElement('a')
  a.setAttribute('href', './posts/' + link['slug'])
  a.setAttribute('target', '_blank')
  a.innerText = link['title'];
  li = document.createElement('li')
  li.appendChild(a)
  document.getElementById('post_link_container').appendChild(li)
}

function loadMore(limit) {
  console.log(currentOffset)
  fetch(host + '/api/post_links' + `?offset=${currentOffset}&limit=${limit}`).then(resp => {
    resp.json().then(data => {
      for (item of data) {
        renderPostItem(item);
      }
      currentOffset += limit;
    });
  });
}
