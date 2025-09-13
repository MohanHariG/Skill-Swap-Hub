function getCsrfToken(){
  const el = document.querySelector('meta[name="csrf-token"]');
  return el ? el.getAttribute('content') : '';
}

document.addEventListener('click', async (e)=>{
  const btn = e.target.closest('.connect-btn');
  if(!btn) return;

  e.preventDefault();
  const postId = btn.dataset.post;
  const form = btn.closest('form');
  const url = form.getAttribute('action');
  const csrftoken = getCsrfToken();

  try{
    const res = await fetch(url, {
      method:'POST',
      headers:{'X-CSRFToken': csrftoken},
    });
    const data = await res.json();
    if(data.ok){
      btn.textContent = 'Requested';
      btn.disabled = true;
    }else{
      alert(data.error || 'Failed');
    }
  }catch(err){
    alert('Network error');
  }
});
