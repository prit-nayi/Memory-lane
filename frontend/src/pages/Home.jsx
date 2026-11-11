import { FiArrowRight, FiHeart, FiImage, FiLock, FiStar } from 'react-icons/fi'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <FiHeart aria-hidden="true" /> A little place for your memories
          </span>
          <h1>
            Every picture
            <br />
            tells a story.
            <br />
            <em>Keep yours close.</em>
          </h1>
          <p>
            Share a favorite moment with the people who make this place special.
            Valid photos join the Memory Lane slideshow as soon as they upload.
          </p>
          <div className="hero-actions">
            <Link className="button-primary" to="/register">
              Share your photos <FiArrowRight aria-hidden="true" />
            </Link>
            <Link className="button-secondary" to="/returning">
              I have an access code
            </Link>
          </div>
          <p className="home-note">
            <FiLock aria-hidden="true" /> Your photos stay connected to your
            private access code.
          </p>
        </div>
        <div className="hero-art" aria-hidden="true">
          <span className="sun-disc" />
          <span className="hero-sparkle one">✳</span>
          <figure className="photo-frame">
            <img src="/images/memory-lane-hero.svg" alt="" />
            <figcaption className="frame-caption">A day to remember</figcaption>
          </figure>
          <span className="hero-sparkle two">✳</span>
        </div>
      </section>

      <section className="home-details" aria-label="How Memory Lane works">
        <div className="detail-item">
          <span className="detail-icon">
            <FiImage aria-hidden="true" />
          </span>
          <div>
            <strong>Share a moment</strong>
            <span>Choose your favorite photos and send them our way.</span>
          </div>
        </div>
        <div className="detail-item">
          <span className="detail-icon">
            <FiLock aria-hidden="true" />
          </span>
          <div>
            <strong>Keep your code</strong>
            <span>Return anytime to see your collection on the slideshow.</span>
          </div>
        </div>
        <div className="detail-item">
          <span className="detail-icon">
            <FiStar aria-hidden="true" />
          </span>
          <div>
            <strong>Relive it together</strong>
            <span>Your validated photos appear on our shared slideshow right away.</span>
          </div>
        </div>
      </section>
    </div>
  )
}
