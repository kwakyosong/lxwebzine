// 우리 웹진에서 JS가 하는 일: 링크 복사, YouTube 누르면 재생, 모바일 하단 고정 CTA
// 버튼 안내 글자는 페이지 언어(<html lang>)대로 쓴다. 새 언어는 규칙/언어.md 표대로 여기에 더한다
var UI_ALL = {
  ko: { copied: '링크를 복사했습니다', noId: 'YouTube 영상 ID를 넣으면 여기서 재생됩니다', yt: 'YouTube 영상', play: '영상 재생', pause: '영상 멈추기', soundOn: '소리 켜기', soundOff: '소리 끄기' },
  en: { copied: 'Link copied', noId: 'Add a YouTube video ID to play it here', yt: 'YouTube video', play: 'Play video', pause: 'Pause video', soundOn: 'Turn sound on', soundOff: 'Turn sound off' },
  ja: { copied: 'リンクをコピーしました', noId: 'YouTubeの動画IDを入れるとここで再生されます', yt: 'YouTube動画', play: '動画を再生', pause: '動画を一時停止', soundOn: '音をオンにする', soundOff: '音をオフにする' },
  zh: { copied: '链接已复制', noId: '填入YouTube视频ID后即可在此播放', yt: 'YouTube视频', play: '播放视频', pause: '暂停视频', soundOn: '打开声音', soundOff: '关闭声音' }
};
var UI = UI_ALL[document.documentElement.lang] || UI_ALL.ko;

(function () {
  // 링크 복사
  document.querySelectorAll('[data-share="copy"]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = document.querySelector('link[rel="canonical"]');
      var text = url ? url.href : location.href;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () { btn.setAttribute('aria-label', UI.copied); });
      }
    });
  });

  // YouTube: 처음엔 썸네일만, 누르면 플레이어를 불러온다
  document.querySelectorAll('.yt').forEach(function (box) {
    box.addEventListener('click', function () {
      var id = box.getAttribute('data-youtube-id');
      if (!id) { box.querySelector('.yt-note').textContent = UI.noId; return; }
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
      f.title = box.getAttribute('aria-label') || UI.yt;
      f.allow = 'autoplay; encrypted-media; picture-in-picture';
      f.allowFullscreen = true;
      box.appendChild(f);
    }, { once: false });
  });

  // 모바일: 히어로 CTA가 화면에서 사라지면 하단 고정 CTA를 보여준다
  var heroCta = document.querySelector('[data-track="hero_cta"]');
  var sticky = document.querySelector('.sticky-cta');
  if (heroCta && sticky && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      sticky.classList.toggle('is-on', !entries[0].isIntersecting);
    }).observe(heroCta);
  }
})();

// 카드뉴스형: 이전·다음 버튼과 번호
document.querySelectorAll('.cardnews').forEach(function (cn) {
  var track = cn.querySelector('.cn-track'), cards = cn.querySelectorAll('.cn-card'), count = cn.querySelector('.cn-count');
  function idx() { return Math.round(track.scrollLeft / (cards[0].offsetWidth + 12)); }
  function show() { count.textContent = (idx() + 1) + ' / ' + cards.length; }
  cn.querySelector('[data-track="card_prev"]').addEventListener('click', function () { track.scrollBy({ left: -(cards[0].offsetWidth + 12), behavior: 'smooth' }); });
  cn.querySelector('[data-track="card_next"]').addEventListener('click', function () { track.scrollBy({ left: cards[0].offsetWidth + 12, behavior: 'smooth' }); });
  track.addEventListener('scroll', show); show();
});

// 무음 영상: 멈춤 버튼, '움직임 줄이기'를 켠 사람에게는 자동 재생하지 않는다
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.clip').forEach(function (fig) {
    var v = fig.querySelector('video'), b = fig.querySelector('.clip-stop');
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); b.setAttribute('aria-pressed', 'true'); b.setAttribute('aria-label', UI.play); b.textContent = '▶'; }
    b.addEventListener('click', function () {
      if (v.paused) { v.play(); b.setAttribute('aria-pressed', 'false'); b.setAttribute('aria-label', UI.pause); b.textContent = '❚❚'; }
      else { v.pause(); b.setAttribute('aria-pressed', 'true'); b.setAttribute('aria-label', UI.play); b.textContent = '▶'; }
    });
  });
})();

// 배경음악: 누를 때만 소리를 켜고 끈다 (자동 재생 없음)
(function () {
  var a = document.querySelector('audio.bgm'), b = document.querySelector('.bgm-toggle');
  if (!a || !b) return;
  b.addEventListener('click', function () {
    if (a.paused) { a.play(); b.setAttribute('aria-pressed', 'true'); b.setAttribute('aria-label', UI.soundOff); }
    else { a.pause(); b.setAttribute('aria-pressed', 'false'); b.setAttribute('aria-label', UI.soundOn); }
  });
})();
