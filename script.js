const landingHero = document.querySelector('#home.hero');

if (landingHero) {
  const heroBackgrounds = [
    { src: 'images/landing-observatory.webp', size: 'cover', position: 'center' },
    { src: 'images/hero-celestial-option-1.png', size: 'cover', position: 'center' },
    { src: 'images/hero-celestial-2026.webp', size: 'cover', position: 'center' },
    {
      src: 'images/background.webp',
      size: 'auto 100%',
      position: 'right center',
      mobilePosition: 'center center'
    }
  ];
  const rotationKey = 'apotheosisHeroBackgroundIndex';
  let heroIndex = 0;

  try {
    const previousIndex = Number.parseInt(localStorage.getItem(rotationKey), 10);
    heroIndex = Number.isInteger(previousIndex)
      ? (previousIndex + 1) % heroBackgrounds.length
      : 0;
    localStorage.setItem(rotationKey, String(heroIndex));
  } catch (error) {
    heroIndex = Math.floor(Math.random() * heroBackgrounds.length);
  }

  const activeHero = heroBackgrounds[heroIndex];
  landingHero.style.setProperty('--hero-background', `url("${activeHero.src}")`);
  landingHero.style.setProperty('--hero-background-size', activeHero.size);
  landingHero.style.setProperty('--hero-background-position', activeHero.position);
  landingHero.style.setProperty('--hero-background-mobile-position', activeHero.mobilePosition || activeHero.position);

  const nextHeroImage = new Image();
  nextHeroImage.src = heroBackgrounds[(heroIndex + 1) % heroBackgrounds.length].src;
}

const reveals = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('show');
    }
  });
}, { threshold: 0.12 });

reveals.forEach(el => {
  if (el.closest('.hero')) {
    el.classList.add('show');
  } else {
    observer.observe(el);
  }
});

document.querySelectorAll('img').forEach(img => {
  if (!img.hasAttribute('loading') && !img.closest('.hero')) {
    img.setAttribute('loading', 'lazy');
    img.setAttribute('decoding', 'async');
  }
});

if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual';
}

window.addEventListener('load', () => {
  window.scrollTo(0, 0);
});

const menuButton = document.querySelector('.menu');
const navElement = document.querySelector('.nav');

if (menuButton && navElement) {
  menuButton.addEventListener('click', () => {
    const isOpen = navElement.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
  });
}

document.querySelectorAll('.navlinks a').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelector('.nav')?.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

const hiddenSearch = document.querySelector('#hiddenSearch');
const portalNote = document.querySelector('#portalNote');

if (hiddenSearch) {
  hiddenSearch.addEventListener('input', () => {
    const value = hiddenSearch.value.trim();

    if (value === 'DMT') {
      if (portalNote) {
        portalNote.textContent = 'Opening...';
      }
      window.location.href = 'hidden.html';
      return;
    }

    if (portalNote) {
      portalNote.textContent = value.length > 0 ? 'No visible result.' : '';
    }
  });
}

const planButtons = document.querySelectorAll('.join-plan');
const selectedPlanInput = document.querySelector('#selectedPlan');
const signupForm = document.querySelector('#signupForm');
const signupMessage = document.querySelector('#signupMessage');
const accessCodeBox = document.querySelector('#accessCodeBox');
const accessCodeInput = document.querySelector('#accessCode');

const updateMembershipFields = plan => {
  const isPaid = plan === 'plus' || plan === 'plusplus';

  if (accessCodeBox) {
    accessCodeBox.hidden = !isPaid;
  }

  if (!isPaid && accessCodeInput) {
    accessCodeInput.value = '';
  }
};

updateMembershipFields(selectedPlanInput?.value || 'basic');

planButtons.forEach(button => {
  button.addEventListener('click', () => {
    const plan = button.getAttribute('data-plan') || 'basic';
    if (selectedPlanInput) {
      selectedPlanInput.value = plan;
    }
    updateMembershipFields(plan);
    document.querySelector('#signupCard')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (signupMessage) {
      signupMessage.textContent = `Selected plan: ${plan === 'plusplus' ? 'Plus Plus' : plan === 'plus' ? 'Plus' : 'Basic'}`;
    }
  });
});

const handleFormSubmission = async (event, form, messageElement, endpoint, fallbackMessage) => {
  if (!form || !messageElement) {
    return;
  }

  event.preventDefault();
  const formData = new FormData(form);
  const payload = new URLSearchParams(formData);

  messageElement.textContent = 'Submitting...';

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: payload,
      credentials: 'same-origin'
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.message || 'Request failed');
    }

    messageElement.textContent = data.message || fallbackMessage;
    if (data.payment?.status === 'redirect' && data.payment.checkout_url) {
      window.location.assign(data.payment.checkout_url);
    }
  } catch (error) {
    messageElement.textContent = error.message === 'Request failed' || error instanceof TypeError
      ? fallbackMessage
      : error.message;
  }
};

if (signupForm) {
  signupForm.addEventListener('submit', event => {
    handleFormSubmission(
      event,
      signupForm,
      signupMessage,
      '/api/register',
      'Thanks for your interest. Please reach out directly at mike@apotheosischurch.org for membership details.'
    );
  });
}

const donationForm = document.querySelector('#donationForm');
const donationMessage = document.querySelector('#donationMessage');

if (donationForm) {
  donationForm.addEventListener('submit', event => {
    handleFormSubmission(
      event,
      donationForm,
      donationMessage,
      '/api/donate',
      'Thank you for your generosity. Please contact us directly at mike@apotheosischurch.org for support options.'
    );
  });
}

const galleryContainer = document.querySelector('#imageGallery');
const galleryImages = [
  { src: 'images/landing-observatory.webp', title: 'Rise Beyond', text: 'The luminous horizon of the homepage journey.' },
  { src: 'images/meditation-mountains.webp', title: 'Purpose of Life', text: 'Reflection opening a path toward growth and direction.' },
  { src: 'images/ideas-matter-background.webp', title: 'Ideas That Matter', text: 'Thought becoming character through living patterns.' },
  { src: 'images/questions.webp', title: 'Four Questions for the Path', text: 'Shared inquiry guided by observation and wonder.' },
  { src: 'images/348dadc9-395b-43fd-a49e-e70e379cd0bc.png', title: 'Growth Is Rarely Straight', text: 'Recursive patterns of becoming and return.' },
  { src: 'images/journey-together.webp', title: 'The Path', text: 'Disciplined movement toward a clearer horizon.' },
  { src: 'images/consciousness.webp', title: 'Consciousness', text: 'The mystery of awareness made visible.' },
  { src: 'images/community-campfire.webp', title: 'Community', text: 'Belonging, reflection, and growth shared in community.' },
  { src: 'images/volunteer-outreach.webp', title: 'Get Involved', text: 'Participation becoming meaningful action.' },
  { src: 'images/tree-of-growth.webp', title: 'Rooted in Experience', text: 'Wisdom rooted in experience and care.' },
  { src: 'images/group-together.webp', title: 'Community Circle', text: 'Conversation, reflection, and belonging practiced together.' },
  { src: 'images/membership-circles.webp', title: 'Membership', text: 'Deeper circles of belonging and participation.' },
  { src: 'images/apoth-library-2026.webp', title: 'Library', text: 'A living archive connected across time.' },
  { src: 'images/cosmic-observatory.webp', title: 'Inquiry', text: 'Observation opening into testable possibilities.' },
  { src: 'images/outreach.webp', title: 'Outreach', text: 'Connection reaching across distance and difference.' },
  { src: 'images/helping-hand.webp', title: 'Support the Mission', text: 'Shared strength sustaining future growth.' },
  { src: 'images/relationships.webp', title: 'Relationships', text: 'A reminder that growth is relational.' },
  { src: 'images/w62mB.webp', title: 'Every Generation', text: 'What we model today shapes what follows.' },
  { src: 'images/two-worlds-village.png', title: 'Partnership', text: 'A practical place of shelter, dignity, and renewal.' },
  { src: 'images/apotheosis-partnership.png', title: 'Two Worlds Together', text: 'Service strengthened through partnership.' }
];

if (galleryContainer) {
  galleryContainer.innerHTML = galleryImages.map(item => `
    <article class="gallery-card reveal">
      <img src="${item.src}" alt="${item.title}" loading="lazy" decoding="async">
      <div>
        <h3>${item.title}</h3>
        <p>${item.text}</p>
      </div>
    </article>
  `).join('');
}
