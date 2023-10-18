function deletePost(postId) {
    fetch('/deletepost', {
    method: 'POST',
    body: JSON.stringify({ postId: postId})
    }).then((_res) => {
        window.location.href="/post"
    });
}