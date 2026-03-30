import { Link } from 'react-router-dom';
import { ArrowRight, Users, DollarSign, Zap, Shield, Globe, BarChart3 } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero-section">
        <div className="hero-glow" />
        <div className="hero-content">
          <span className="hero-badge">⚡ Expense Splitting Made Simple</span>
          <h1 className="hero-title">
            Split expenses.<br />
            <span className="hero-gradient">Not friendships.</span>
          </h1>
          <p className="hero-subtitle">
            Track group expenses, simplify debts with one click, and never argue
            about who owes what again. Powered by graph-based debt minimization.
          </p>
          <div className="hero-actions">
            <Link to="/register" className="btn btn-primary btn-lg">
              Get Started Free <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="btn btn-ghost btn-lg">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <h2 className="section-title">Everything you need to split fair</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon"><Users size={24} /></div>
            <h3>Group Management</h3>
            <p>Create groups, invite members, and manage expenses together in real-time.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><DollarSign size={24} /></div>
            <h3>Smart Splitting</h3>
            <p>Equal, percentage, share-based, or exact — four split methods with penny-perfect accuracy.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><Zap size={24} /></div>
            <h3>Debt Simplification</h3>
            <p>Our graph algorithm minimizes transactions — 5 debts become 2 with one click.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><BarChart3 size={24} /></div>
            <h3>Dashboard Analytics</h3>
            <p>See exactly what you owe and are owed, across all groups, at a glance.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><Globe size={24} /></div>
            <h3>Multi-Currency</h3>
            <p>Track expenses in any currency. Forex conversion built-in for global groups.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><Shield size={24} /></div>
            <h3>Recurring Expenses</h3>
            <p>Set it and forget it. Rent, subscriptions, and bills auto-split on schedule.</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <h2>Ready to split fair?</h2>
        <p>Join now and never stress about shared expenses again.</p>
        <Link to="/register" className="btn btn-primary btn-lg">
          Create Your Account <ArrowRight size={18} />
        </Link>
      </section>

      <footer className="landing-footer">
        <p>© {new Date().getFullYear()} Split It Fair — Built with FastAPI & React</p>
      </footer>
    </div>
  );
}
