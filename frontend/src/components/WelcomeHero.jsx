import React from 'react';
import { 
  BookOpen, Users, Home, Sparkles, Trophy, 
  Bell, Award, ArrowUpRight, Compass, Globe, HelpCircle, ExternalLink
} from 'lucide-react';
import { LinkedinIcon, YoutubeIcon, InstagramIcon } from './BrandIcons';

const CATEGORIES = [
  { id: 'academics', label: 'Academics', icon: BookOpen },
  { id: 'student_services', label: 'Student Services', icon: Users },
  { id: 'hostel', label: 'Hostel', icon: Home },
  { id: 'campus_life', label: 'Campus Life', icon: Sparkles },
  { id: 'clubs_events', label: 'Clubs & Events', icon: Trophy },
  { id: 'opportunities', label: 'Opportunities', icon: Award },
  { id: 'announcements', label: 'Announcements', icon: Bell },
];

const EXAMPLE_QUESTIONS = [
  {
    category: 'Hostel',
    question: 'What is the hostel menu for Wednesday?',
    snippet: 'Discover breakfast, lunch, snacks, and dinner served in the PEC mess.'
  },
  {
    category: 'Dress Code',
    question: "What's the dress code on Monday?",
    snippet: 'Verified norms for formal and casual attire on campus.'
  },
  {
    category: 'Academics',
    question: 'How many IATs are conducted each semester?',
    snippet: 'Examination cycles, internal assessments, and preparation schedule.'
  },
  {
    category: 'Innovation & Events',
    question: 'Was there any AI workshop recently?',
    snippet: 'Official updates on hands-on technical workshops and student hackathons.'
  },
  {
    category: 'Campus Life',
    question: 'Which clubs and innovation domains are available?',
    snippet: 'Explore Google Developer Club, Drones Club, Idea Lab, and Robotics.'
  },
  {
    category: 'Hostel Rules',
    question: 'What is the hostel leave procedure and card colors?',
    snippet: 'Requirements for Pink/Yellow leave cards and security signoffs.'
  }
];

export default function WelcomeHero({ onSelectPrompt, onSelectCategory, userProfile, onOpenMyCampus, currentUser, onOpenAuth }) {
  // Tailor sample questions if profile has specific focus
  let activeQuestions = [...EXAMPLE_QUESTIONS];

  if (userProfile?.role === 'prospective_student') {
    activeQuestions = [
      {
        category: 'Admissions',
        question: 'Where is the admissions office and what are the procedures?',
        snippet: 'Official guidance on B.E/B.Tech programmes and college administration.'
      },
      {
        category: 'Campus Facilities',
        question: 'What facilities and laboratories are available on campus?',
        snippet: 'Overview of 45-acre campus, AR-VR CoE, Wi-Fi, and sports amenities.'
      },
      {
        category: 'Placements',
        question: 'What are the placement highlights and top recruiters?',
        snippet: 'Verified records of top recruiters like Zoho, Cognizant, and packages.'
      },
      {
        category: 'Hostel & Mess',
        question: 'What are the hostel accommodation facilities and mess menu?',
        snippet: 'Hygienic rooms, food menus, Wi-Fi, and security protocols.'
      },
      {
        category: 'Innovation',
        question: 'What clubs and innovation domains are available?',
        snippet: 'Explore 13 Innovation Domains, Google Developer Club, and Idea Lab.'
      },
      {
        category: 'Dress Code',
        question: "What's the dress code on Monday?",
        snippet: 'Verified norms for formal and casual attire on campus.'
      }
    ];
  } else if (userProfile?.department?.includes('Computer') || userProfile?.department?.includes('Intelligence')) {
    activeQuestions[0] = {
      category: 'AI & Hackathons',
      question: 'Was there any AI workshop or national hackathon recently?',
      snippet: 'Generative AI workshop and PRATHYUSHA IGNITE 2026 hackathon updates.'
    };
  }

  return (
    <div style={{
      maxWidth: '860px',
      margin: '0 auto',
      padding: '36px 20px 24px 20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center'
    }}>
      {/* 1. Large Prathyusha Engineering College Logo */}
      <div style={{
        position: 'relative',
        marginBottom: '20px',
        backgroundColor: '#FFFFFF',
        padding: '12px 32px',
        borderRadius: '16px',
        border: '1.5px solid var(--accent-gold)',
        boxShadow: 'var(--shadow-md)',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <img
          src="/college_logo.jpeg"
          alt="Prathyusha Engineering College"
          style={{
            maxWidth: '300px',
            width: '100%',
            height: 'auto',
            maxHeight: '80px',
            objectFit: 'contain',
            display: 'block'
          }}
        />
      </div>

      {/* 2. Welcome Title & Tagline */}
      <h1 style={{
        fontFamily: 'var(--font-display)',
        fontWeight: 800,
        fontSize: '2.5rem',
        letterSpacing: '0.08em',
        color: 'var(--accent-burgundy)',
        marginBottom: '8px'
      }}>
        CAMPUSIQ
      </h1>

      <p style={{
        fontFamily: 'var(--font-serif)',
        fontStyle: 'italic',
        fontSize: '1.22rem',
        color: 'var(--text-primary)',
        marginBottom: '10px'
      }}>
        Your campus, one conversation away.
      </p>

      <p style={{
        fontSize: '0.94rem',
        color: 'var(--text-muted)',
        maxWidth: '580px',
        lineHeight: 1.55,
        marginBottom: '18px'
      }}>
        Ask about academics, student services, campus life, hostel information, clubs, events, announcements, opportunities, and other verified college information.
      </p>

      {/* Entry Mode Status & Subtle Switcher */}
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '12px',
        padding: '6px 16px',
        backgroundColor: 'var(--bg-secondary)',
        borderRadius: '24px',
        border: '1px solid var(--border-subtle)',
        marginBottom: '30px'
      }}>
        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Signed in as <strong style={{ color: 'var(--accent-burgundy)' }}>{currentUser.name}</strong>
            </span>
          </div>
        ) : (
          <>
            <span style={{
              fontSize: '0.80rem',
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: 'var(--accent-gold)' }} />
              Browsing as <strong>Guest</strong>
            </span>
            <span style={{ color: 'var(--border-subtle)' }}>•</span>
            <button
              onClick={onOpenAuth}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-burgundy)',
                fontWeight: 700,
                fontSize: '0.80rem',
                cursor: 'pointer',
                padding: '2px 4px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              Sign In / Create Account
            </button>
          </>
        )}
      </div>

      {/* 3. Explore CampusIQ Knowledge Categories */}
      <div style={{ width: '100%', marginBottom: '32px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          fontSize: '0.78rem',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
          marginBottom: '14px'
        }}>
          <Compass size={14} color="var(--accent-burgundy)" />
          <span>Explore CampusIQ Knowledge</span>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          justifyContent: 'center'
        }}>
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            return (
              <button
                key={cat.id}
                onClick={() => onSelectCategory(cat.label)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '7px 14px',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.84rem',
                  fontWeight: 500,
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.18s ease',
                  boxShadow: 'var(--shadow-sm)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
                  e.currentTarget.style.color = 'var(--accent-burgundy)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <Icon size={14} color="var(--accent-burgundy)" />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. What Can I Ask? Sample Question Cards */}
      <div style={{ width: '100%', marginBottom: '32px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          fontSize: '0.78rem',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
          marginBottom: '14px'
        }}>
          <HelpCircle size={14} color="var(--accent-burgundy)" />
          <span>What Can I Ask?</span>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '12px',
          textAlign: 'left'
        }}>
          {activeQuestions.map((ex, idx) => (
            <div
              key={idx}
              onClick={() => onSelectPrompt(ex.question)}
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 16px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                boxShadow: 'var(--shadow-sm)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
                e.currentTarget.style.transform = 'translateY(-3px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-subtle)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
              }}
            >
              <div>
                <div style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  color: 'var(--accent-rose)',
                  marginBottom: '4px'
                }}>
                  {ex.category}
                </div>
                <div style={{
                  fontSize: '0.92rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  lineHeight: 1.35,
                  marginBottom: '6px'
                }}>
                  {ex.question}
                </div>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginTop: '8px'
              }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  {ex.snippet}
                </span>
                <ArrowUpRight size={14} color="var(--accent-burgundy)" style={{ flexShrink: 0 }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Official College Links (Only Verified Usable Links) */}
      <div style={{ width: '100%' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          fontSize: '0.78rem',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
          marginBottom: '14px'
        }}>
          <Globe size={14} color="var(--accent-burgundy)" />
          <span>Official College Links</span>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '10px',
          justifyContent: 'center'
        }}>
          <a
            href="https://prathyusha.edu.in"
            target="_blank"
            rel="noopener noreferrer"
            style={linkBtnStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
              e.currentTarget.style.color = 'var(--accent-burgundy)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <Globe size={14} color="var(--accent-burgundy)" />
            <span>College Website</span>
            <ExternalLink size={12} color="var(--text-muted)" />
          </a>

          <a
            href="https://www.linkedin.com/school/prathyushaenggcollege/"
            target="_blank"
            rel="noopener noreferrer"
            style={linkBtnStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
              e.currentTarget.style.color = 'var(--accent-burgundy)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <LinkedinIcon size={14} color="#0A66C2" />
            <span>LinkedIn</span>
            <ExternalLink size={12} color="var(--text-muted)" />
          </a>

          <a
            href="https://youtube.com/@prathyushaengineeringcollege/"
            target="_blank"
            rel="noopener noreferrer"
            style={linkBtnStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
              e.currentTarget.style.color = 'var(--accent-burgundy)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <YoutubeIcon size={14} color="#FF0000" />
            <span>YouTube</span>
            <ExternalLink size={12} color="var(--text-muted)" />
          </a>

          <a
            href="https://www.instagram.com/prathyushainstitute/"
            target="_blank"
            rel="noopener noreferrer"
            style={linkBtnStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-burgundy)';
              e.currentTarget.style.color = 'var(--accent-burgundy)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <InstagramIcon size={14} color="#E4405F" />
            <span>Instagram</span>
            <ExternalLink size={12} color="var(--text-muted)" />
          </a>
        </div>
      </div>
    </div>
  );
}

const linkBtnStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '7px',
  padding: '7px 16px',
  backgroundColor: 'var(--bg-card)',
  border: '1px solid var(--border-subtle)',
  borderRadius: 'var(--radius-full)',
  fontSize: '0.82rem',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  textDecoration: 'none',
  transition: 'all 0.18s ease',
  boxShadow: 'var(--shadow-sm)'
};

