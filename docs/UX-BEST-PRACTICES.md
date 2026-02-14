# CivicQ UX Best Practices
## Insights from YouTube and Reddit Design Patterns

**Document Version:** 1.0
**Last Updated:** 2026-02-14
**Purpose:** Research-based recommendations for improving CivicQ's user experience by applying proven patterns from YouTube and Reddit.

---

## Executive Summary

This document analyzes best UX practices from YouTube and Reddit and provides specific, actionable recommendations for CivicQ. These platforms excel at content discovery, engagement, and mobile responsiveness—all critical for CivicQ's mission to make local democracy more accessible.

**Key Themes:**
- **Navigation:** Persistent, accessible, minimal
- **Content Organization:** Card-based, scannable, hierarchical
- **User Engagement:** Voting mechanisms, feedback, personalization
- **Mobile-First:** Touch-optimized, responsive, progressive
- **Performance:** Loading states, skeleton screens, optimistic UI
- **Error Handling:** Graceful, actionable, contextual

---

## 1. Navigation Patterns

### YouTube & Reddit Approach

#### Sticky Headers
Both platforms use **persistent navigation** that remains accessible during scrolling:

- **YouTube:** Sticky header with logo, search, and user actions (notifications, profile)
- **Reddit:** Sticky header on desktop; bottom navigation on mobile
- **Best Practice:** Headers contain 3-5 core actions maximum to prevent clutter
- **Mobile Pattern:** Auto-hide on scroll down, reappear on scroll up to maximize content space

**Research Finding:** Sticky headers improve discoverability and reduce the need to scroll back to top, but must be carefully implemented to avoid accessibility issues with keyboard navigation and screen readers.

#### Sidebar Patterns
- **YouTube (Desktop):** Fixed left sidebar with primary navigation (Home, Shorts, Subscriptions) that can collapse
- **Reddit (Desktop):** Right sidebar for contextual information (subreddit rules, stats); main navigation in sticky header
- **Mobile:** Both platforms replace sidebars with bottom navigation bars or hamburger menus

**Key Principle:** Keep primary navigation fixed and always accessible, but don't let it obstruct content on smaller screens.

### Current CivicQ Implementation

```tsx
// From Layout.tsx (lines 21-62)
<nav className="bg-white shadow-sm border-b border-gray-200">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex justify-between h-16">
      <div className="flex items-center">
        <Link to="/" className="flex items-center">
          <span className="text-2xl font-bold text-civic-blue">CivicQ</span>
        </Link>
        <div className="hidden md:ml-10 md:flex md:space-x-8">
          <Link to="/ballot" className="text-gray-700 hover:text-civic-blue...">
            My Ballot
          </Link>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        {/* Auth controls */}
      </div>
    </div>
  </div>
</nav>
```

**Status:** Good foundation with responsive design, but not sticky.

### Recommendations for CivicQ

#### 1.1 Implement Sticky Navigation with Smart Behavior

```tsx
// Recommended: Smart sticky header that hides on scroll down, shows on scroll up
const [isVisible, setIsVisible] = useState(true);
const [lastScrollY, setLastScrollY] = useState(0);

useEffect(() => {
  const handleScroll = () => {
    const currentScrollY = window.scrollY;

    // Show header when scrolling up or at top
    if (currentScrollY < lastScrollY || currentScrollY < 100) {
      setIsVisible(true);
    }
    // Hide header when scrolling down (but not in forms or interactive areas)
    else if (currentScrollY > lastScrollY && currentScrollY > 100) {
      setIsVisible(false);
    }

    setLastScrollY(currentScrollY);
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  return () => window.removeEventListener('scroll', handleScroll);
}, [lastScrollY]);

return (
  <nav className={`
    sticky top-0 z-50
    bg-white shadow-sm border-b border-gray-200
    transition-transform duration-300
    ${isVisible ? 'translate-y-0' : '-translate-y-full'}
  `}>
    {/* Nav content */}
  </nav>
);
```

**Benefits:**
- Header always accessible with scroll-up gesture
- Maximizes content viewing area on scroll down
- Smooth, modern interaction pattern users expect

#### 1.2 Add Quick Navigation Shortcuts

Expand the navigation to include frequently accessed items:

```tsx
<div className="hidden md:ml-10 md:flex md:space-x-8">
  <Link to="/ballot" className="...">My Ballot</Link>
  <Link to="/questions" className="...">Questions</Link>
  <Link to="/candidates" className="...">Candidates</Link>
  {/* Maximum 5 items */}
</div>
```

#### 1.3 Mobile Bottom Navigation

For mobile users, implement a bottom navigation bar (like Reddit mobile):

```tsx
// MobileBottomNav.tsx
<nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
  <div className="flex justify-around py-2">
    <NavItem icon={HomeIcon} label="Home" to="/" />
    <NavItem icon={BallotIcon} label="Ballot" to="/ballot" />
    <NavItem icon={QuestionIcon} label="Questions" to="/questions" />
    <NavItem icon={UserIcon} label="Profile" to="/profile" />
  </div>
</nav>
```

**Rationale:** Bottom navigation is 300% faster to access on mobile devices compared to top navigation (thumb-friendly zone).

#### 1.4 Breadcrumb Navigation

For deep navigation (Contest > Question > Answer), add breadcrumbs:

```tsx
<nav className="mb-4" aria-label="Breadcrumb">
  <ol className="flex items-center space-x-2 text-sm">
    <li><Link to="/ballot" className="text-civic-blue">My Ballot</Link></li>
    <li className="text-gray-400">/</li>
    <li><Link to={`/contest/${contestId}`} className="text-civic-blue">Mayor Race</Link></li>
    <li className="text-gray-400">/</li>
    <li className="text-gray-700">Question #42</li>
  </ol>
</nav>
```

---

## 2. Content Organization

### YouTube & Reddit Approach

#### Card-Based Layouts
Both platforms use **card-based design** for content organization:

- **YouTube:** Video cards with thumbnail, title, channel info, view count, timestamp
- **Reddit:** Post cards with voting, title, metadata (subreddit, author, time), preview
- **Bento Grid Pattern (2026 Trend):** Content organized in sleek, rounded rectangular cards designed for quick scanning

**Research Finding:** Card-based layouts are the most popular UI pattern for content feeds because they're flexible, scannable, and work across all device sizes.

#### Hierarchy & Scanning
- **Visual Hierarchy:** Clear distinction between primary (title), secondary (metadata), and tertiary (stats) information
- **Whitespace:** Generous padding prevents cognitive overload
- **Grouping:** Related content grouped logically (e.g., YouTube's "Recommended," Reddit's "Popular")

### Current CivicQ Implementation

```tsx
// QuestionCard.tsx - Good card structure
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
  <div className="flex items-start space-x-4">
    <VoteButton questionId={question.id} />
    <div className="flex-1">
      <Link to={`/question/${question.id}`} className="text-lg font-semibold...">
        {question.question_text}
      </Link>
      {/* Metadata */}
    </div>
  </div>
</div>
```

**Status:** Good foundation with clear hierarchy and card design.

### Recommendations for CivicQ

#### 2.1 Enhance Visual Hierarchy

Add visual distinction for different content types:

```tsx
// Enhanced QuestionCard with better hierarchy
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6
              hover:shadow-md hover:border-civic-blue transition-all duration-200">
  <div className="flex items-start space-x-4">
    {/* Vote section - more prominent */}
    <div className="flex-shrink-0">
      <VoteButton questionId={question.id} netVotes={netVotes} />
    </div>

    {/* Content section */}
    <div className="flex-1 min-w-0"> {/* min-w-0 prevents flex overflow */}
      {/* Primary: Question text */}
      <Link to={`/question/${question.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-civic-blue
                       line-clamp-2"> {/* Limit to 2 lines for consistency */}
        {question.question_text}
      </Link>

      {/* Secondary: Context */}
      {question.context && (
        <p className="mt-2 text-sm text-gray-600 italic line-clamp-2">
          {question.context}
        </p>
      )}

      {/* Tertiary: Tags */}
      {question.issue_tags && question.issue_tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {question.issue_tags.slice(0, 3).map((tag) => (
            <span key={tag} className="inline-flex items-center px-2.5 py-0.5
                                       rounded-full text-xs font-medium
                                       bg-blue-100 text-blue-800 hover:bg-blue-200
                                       cursor-pointer transition-colors">
              {tag}
            </span>
          ))}
          {question.issue_tags.length > 3 && (
            <span className="text-xs text-gray-500">+{question.issue_tags.length - 3} more</span>
          )}
        </div>
      )}

      {/* Metadata bar */}
      <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
        <span className="flex items-center">
          <ArrowUpIcon className="w-4 h-4 mr-1" />
          {netVotes} votes
        </span>
        {question.video_answers && question.video_answers.length > 0 && (
          <span className="flex items-center">
            <VideoIcon className="w-4 h-4 mr-1" />
            {question.video_answers.length} answers
          </span>
        )}
        <span className="flex items-center">
          <ClockIcon className="w-4 h-4 mr-1" />
          {formatTimeAgo(question.created_at)}
        </span>
        <StatusBadge status={question.status} />
      </div>
    </div>
  </div>
</div>
```

#### 2.2 Implement Feed Sections with Clear Headers

Organize content like YouTube's homepage:

```tsx
// BallotPage.tsx enhancement
<div className="container mx-auto px-4 py-8">
  {/* Section: High Priority Races */}
  <Section
    title="High Priority Races"
    subtitle="Contests with the most community engagement"
    icon={<FireIcon />}
  >
    <div className="grid gap-6">
      {priorityRaces.map(race => <ContestCard key={race.id} contest={race} />)}
    </div>
  </Section>

  {/* Section: All Races */}
  <Section
    title="All Races"
    subtitle={`${races.length} contests on your ballot`}
  >
    <div className="grid gap-6">
      {races.map(race => <ContestCard key={race.id} contest={race} />)}
    </div>
  </Section>

  {/* Section: Ballot Measures */}
  <Section
    title="Ballot Measures"
    subtitle="Vote yes or no on these propositions"
  >
    <div className="grid gap-6">
      {measures.map(measure => <ContestCard key={measure.id} contest={measure} />)}
    </div>
  </Section>
</div>

// Section component
const Section = ({ title, subtitle, icon, children }) => (
  <section className="mb-12">
    <div className="flex items-center mb-6">
      {icon && <div className="mr-3 text-civic-blue">{icon}</div>}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
      </div>
    </div>
    {children}
  </section>
);
```

#### 2.3 Grid vs. List Toggle

Allow users to choose their view preference (like YouTube):

```tsx
const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');

<div className="flex justify-between items-center mb-6">
  <h2 className="text-2xl font-bold">Questions</h2>
  <div className="flex space-x-2">
    <button
      onClick={() => setViewMode('list')}
      className={`p-2 rounded ${viewMode === 'list' ? 'bg-civic-blue text-white' : 'bg-gray-100'}`}
      aria-label="List view"
    >
      <ListIcon className="w-5 h-5" />
    </button>
    <button
      onClick={() => setViewMode('grid')}
      className={`p-2 rounded ${viewMode === 'grid' ? 'bg-civic-blue text-white' : 'bg-gray-100'}`}
      aria-label="Grid view"
    >
      <GridIcon className="w-5 h-5" />
    </button>
  </div>
</div>

<div className={viewMode === 'grid'
  ? 'grid grid-cols-1 md:grid-cols-2 gap-6'
  : 'space-y-4'
}>
  {questions.map(q => <QuestionCard key={q.id} question={q} compact={viewMode === 'grid'} />)}
</div>
```

#### 2.4 Add Filter and Sort Controls

Like Reddit's sort options (Hot, New, Top, Rising):

```tsx
<div className="flex flex-wrap gap-3 mb-6">
  <SortButton
    active={sortBy === 'votes'}
    onClick={() => setSortBy('votes')}
    icon={<TrendingIcon />}
  >
    Top Voted
  </SortButton>
  <SortButton
    active={sortBy === 'recent'}
    onClick={() => setSortBy('recent')}
    icon={<ClockIcon />}
  >
    Recent
  </SortButton>
  <SortButton
    active={sortBy === 'unanswered'}
    onClick={() => setSortBy('unanswered')}
    icon={<QuestionIcon />}
  >
    Unanswered
  </SortButton>
  <SortButton
    active={sortBy === 'answered'}
    onClick={() => setSortBy('answered')}
    icon={<VideoIcon />}
  >
    Answered
  </SortButton>
</div>
```

---

## 3. User Engagement

### YouTube & Reddit Approach

#### Voting Mechanisms
- **Reddit:** Upvote/downvote buttons prominently placed, vote count visible, color-coded (orange/blue)
- **YouTube:** Like/dislike (historical), subscribe button, notification bell
- **Interaction Feedback:** Immediate visual feedback on click (color change, animation)

#### Vote To Promote Pattern
**Research Finding:** The Vote To Promote pattern allows users to democratically decide what content is more popular. Displaying the number of votes gives visitors clear indication of popularity and enables comparison.

#### Engagement Features
- **Comments:** Threaded discussions (Reddit has nested replies, YouTube recently added thread visualization in 2026)
- **Personalization:** Recommended content based on viewing history
- **Notifications:** Real-time updates on replies, votes, new content
- **Sharing:** Easy sharing to social platforms

### Current CivicQ Implementation

```tsx
// VoteButton.tsx - Good foundation
<div className="flex flex-col items-center space-y-1">
  <button onClick={handleUpvote} className={hasUpvoted ? 'text-civic-green' : 'text-gray-400'}>
    <svg className="w-6 h-6" fill={hasUpvoted ? 'currentColor' : 'none'}>
      {/* Upvote icon */}
    </svg>
  </button>
  <button onClick={handleDownvote} className={hasDownvoted ? 'text-red-500' : 'text-gray-400'}>
    <svg className="w-6 h-6" fill={hasDownvoted ? 'currentColor' : 'none'}>
      {/* Downvote icon */}
    </svg>
  </button>
</div>
```

**Status:** Clean implementation, but missing vote count display and animation feedback.

### Recommendations for CivicQ

#### 3.1 Enhanced Vote Button with Visual Feedback

```tsx
// Enhanced VoteButton with count and animations
const VoteButton: React.FC<VoteButtonProps> = ({ questionId, netVotes, userVote }) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const { upvote, downvote, isVoting } = useVote(questionId);

  const handleVote = async (value: 1 | -1) => {
    if (!isAuthenticated) {
      toast.error('Please log in to vote');
      return;
    }

    setIsAnimating(true);
    await (value === 1 ? upvote() : downvote());
    setTimeout(() => setIsAnimating(false), 300);
  };

  return (
    <div className="flex flex-col items-center">
      {/* Upvote */}
      <button
        onClick={() => handleVote(1)}
        disabled={isVoting}
        className={`
          p-2 rounded-lg transition-all duration-200
          ${userVote === 1
            ? 'text-civic-green bg-green-50 scale-110'
            : 'text-gray-400 hover:bg-gray-100 hover:text-civic-green'}
          ${isAnimating && userVote === 1 ? 'animate-bounce' : ''}
          ${isVoting ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}
        `}
        aria-label="Upvote"
      >
        <ArrowUpIcon className="w-6 h-6" />
      </button>

      {/* Vote count */}
      <span className={`
        px-2 py-1 text-sm font-bold rounded
        transition-all duration-200
        ${netVotes > 0 ? 'text-civic-green' : netVotes < 0 ? 'text-red-500' : 'text-gray-600'}
        ${isAnimating ? 'scale-125' : ''}
      `}>
        {netVotes > 0 ? '+' : ''}{netVotes}
      </span>

      {/* Downvote */}
      <button
        onClick={() => handleVote(-1)}
        disabled={isVoting}
        className={`
          p-2 rounded-lg transition-all duration-200
          ${userVote === -1
            ? 'text-red-500 bg-red-50 scale-110'
            : 'text-gray-400 hover:bg-gray-100 hover:text-red-500'}
          ${isAnimating && userVote === -1 ? 'animate-bounce' : ''}
          ${isVoting ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}
        `}
        aria-label="Downvote"
      >
        <ArrowDownIcon className="w-6 h-6" />
      </button>
    </div>
  );
};
```

#### 3.2 Add Engagement Indicators

Show activity level on cards (like Reddit's awards, YouTube's trending):

```tsx
<div className="flex items-center space-x-3 text-sm">
  {/* High engagement indicator */}
  {netVotes > 50 && (
    <span className="flex items-center px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
      <FireIcon className="w-4 h-4 mr-1" />
      Hot
    </span>
  )}

  {/* Recently answered */}
  {question.lastAnsweredAt && isRecent(question.lastAnsweredAt) && (
    <span className="flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
      <SparklesIcon className="w-4 h-4 mr-1" />
      New Answer
    </span>
  )}

  {/* Fully answered */}
  {question.video_answers?.length === activeCandidates.length && (
    <span className="flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full">
      <CheckCircleIcon className="w-4 h-4 mr-1" />
      All Answered
    </span>
  )}
</div>
```

#### 3.3 Implement Progress Tracking

Show users their engagement progress (gamification):

```tsx
// User Dashboard Widget
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <h3 className="text-lg font-semibold mb-4">Your Impact</h3>

  <div className="space-y-4">
    <ProgressStat
      label="Questions Submitted"
      value={userStats.questionsSubmitted}
      goal={5}
      icon={<QuestionIcon />}
    />
    <ProgressStat
      label="Votes Cast"
      value={userStats.votesCast}
      goal={20}
      icon={<VoteIcon />}
    />
    <ProgressStat
      label="Contests Reviewed"
      value={userStats.contestsReviewed}
      goal={ballot.contests.length}
      icon={<CheckIcon />}
    />
  </div>

  {userStats.questionsSubmitted >= 5 && (
    <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
      <div className="flex items-center text-green-800">
        <TrophyIcon className="w-5 h-5 mr-2" />
        <span className="text-sm font-medium">Active Citizen Badge Earned!</span>
      </div>
    </div>
  )}
</div>
```

#### 3.4 Add Follow/Bookmark Features

Let users follow specific contests or candidates:

```tsx
// Contest header addition
<button
  onClick={handleFollowContest}
  className="flex items-center px-4 py-2 border border-civic-blue text-civic-blue
             rounded-lg hover:bg-civic-blue hover:text-white transition-colors"
>
  {isFollowing ? (
    <>
      <BellIcon className="w-5 h-5 mr-2 fill-current" />
      Following
    </>
  ) : (
    <>
      <BellIcon className="w-5 h-5 mr-2" />
      Follow
    </>
  )}
</button>

{isFollowing && (
  <p className="text-sm text-gray-600 mt-2">
    You'll be notified when candidates answer questions
  </p>
)}
```

---

## 4. Mobile Responsiveness

### YouTube & Reddit Approach

#### Mobile-First Design (2026 Best Practice)
**Research Finding:** 2026 marks a shift toward experience-first design. Mobile-first approach involves designing for the smallest screens first, then progressively enhancing for larger displays.

#### Touch Targets
- **Minimum Size:** 44x44px (iOS), 48x48px recommended
- **Spacing:** Adequate spacing between interactive elements to prevent misclicks
- **Bottom Placement:** Critical actions in thumb-friendly zones (bottom third of screen)

#### Responsive Patterns
- **YouTube Mobile:**
  - Bottom navigation bar (Home, Shorts, Subscriptions, Library)
  - Swipeable video cards
  - Full-screen video player
  - Collapsible comments section

- **Reddit Mobile:**
  - Bottom tab bar (Home, Popular, Create, Chat, Inbox)
  - Card-based feed optimized for vertical scrolling
  - Expandable posts (tap to view full content)
  - Native-feeling interactions

**Research Finding:** Bottom tab bars work best for 3-5 core actions. Hamburger menus are better for complex hierarchies.

### Current CivicQ Implementation

```tsx
// Layout.tsx - Responsive but no mobile-specific optimizations
<div className="hidden md:ml-10 md:flex md:space-x-8">
  {/* Desktop navigation */}
</div>
```

**Status:** Basic responsiveness with `md:` breakpoints, but lacks mobile-optimized navigation and touch targets.

### Recommendations for CivicQ

#### 4.1 Mobile Bottom Navigation Bar

```tsx
// MobileBottomNav.tsx
const MobileBottomNav: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: HomeIcon, label: 'Home' },
    { path: '/ballot', icon: BallotBoxIcon, label: 'Ballot' },
    { path: '/questions', icon: QuestionMarkIcon, label: 'Questions' },
    { path: '/profile', icon: UserIcon, label: 'Profile' },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-area-bottom">
      <div className="flex justify-around">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`
                flex flex-col items-center justify-center
                flex-1 py-2 min-h-[56px]
                transition-colors duration-200
                ${isActive
                  ? 'text-civic-blue'
                  : 'text-gray-500 active:bg-gray-100'}
              `}
            >
              <Icon className={`w-6 h-6 ${isActive ? 'fill-current' : ''}`} />
              <span className={`text-xs mt-1 ${isActive ? 'font-semibold' : ''}`}>
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
```

**Add to Layout.tsx:**
```tsx
<div className="min-h-screen bg-gray-50 pb-16 md:pb-0">
  {/* Desktop nav */}
  <nav className="hidden md:block sticky top-0 z-50 bg-white...">
    {/* Existing desktop navigation */}
  </nav>

  {/* Content */}
  <main className="flex-grow">{children}</main>

  {/* Mobile bottom nav */}
  <MobileBottomNav />

  {/* Footer - hidden on mobile */}
  <footer className="hidden md:block bg-white border-t...">
    {/* Existing footer */}
  </footer>
</div>
```

#### 4.2 Touch-Optimized Interactive Elements

Ensure all touch targets meet minimum size requirements:

```tsx
// Button component with proper touch targets
const Button: React.FC<ButtonProps> = ({ children, size = 'md', ...props }) => {
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm min-h-[44px]',      // Still meets 44px height
    md: 'px-4 py-3 text-base min-h-[48px]',    // Recommended 48px
    lg: 'px-6 py-4 text-lg min-h-[52px]',
  };

  return (
    <button
      className={`
        ${sizeClasses[size]}
        rounded-lg font-medium
        transition-all duration-200
        active:scale-95
        disabled:opacity-50 disabled:cursor-not-allowed
      `}
      {...props}
    >
      {children}
    </button>
  );
};
```

#### 4.3 Responsive Card Layouts

Optimize cards for different screen sizes:

```tsx
// QuestionCard with responsive layout
<div className="bg-white rounded-lg shadow-sm border border-gray-200
                p-4 md:p-6 hover:shadow-md transition-shadow">
  <div className="flex items-start space-x-3 md:space-x-4">
    {/* Vote section - smaller on mobile */}
    <div className="flex-shrink-0">
      <VoteButton
        questionId={question.id}
        size={isMobile ? 'sm' : 'md'}
      />
    </div>

    {/* Content - responsive typography */}
    <div className="flex-1 min-w-0">
      <Link
        to={`/question/${question.id}`}
        className="text-base md:text-lg font-semibold text-gray-900
                   hover:text-civic-blue line-clamp-3 md:line-clamp-2"
      >
        {question.question_text}
      </Link>

      {/* Context - hidden on mobile if too long */}
      {question.context && (
        <p className="mt-2 text-sm text-gray-600 italic
                      line-clamp-2 md:line-clamp-2">
          {question.context}
        </p>
      )}

      {/* Tags - scrollable on mobile */}
      {question.issue_tags && question.issue_tags.length > 0 && (
        <div className="mt-3 flex gap-2 overflow-x-auto pb-2 md:pb-0
                        scrollbar-hide">
          {question.issue_tags.map((tag) => (
            <span key={tag} className="inline-flex items-center px-2.5 py-0.5
                                       rounded-full text-xs font-medium
                                       bg-blue-100 text-blue-800
                                       whitespace-nowrap flex-shrink-0">
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Metadata - stacked on mobile */}
      <div className="mt-4 flex flex-col sm:flex-row sm:items-center
                      gap-2 sm:gap-4 text-sm text-gray-500">
        <span className="flex items-center">
          <ArrowUpIcon className="w-4 h-4 mr-1" />
          {netVotes} votes
        </span>
        {question.video_answers && question.video_answers.length > 0 && (
          <span className="flex items-center">
            <VideoIcon className="w-4 h-4 mr-1" />
            {question.video_answers.length} answers
          </span>
        )}
        <StatusBadge status={question.status} />
      </div>
    </div>
  </div>
</div>
```

#### 4.4 Swipe Gestures for Mobile

Add swipe gestures for common actions (like Reddit's swipe to upvote):

```tsx
// useSwipeGesture hook
const useSwipeGesture = (onSwipeLeft?: () => void, onSwipeRight?: () => void) => {
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(0);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && onSwipeLeft) onSwipeLeft();
    if (isRightSwipe && onSwipeRight) onSwipeRight();
  };

  return { onTouchStart, onTouchMove, onTouchEnd };
};

// Usage in QuestionCard
const QuestionCard: React.FC<QuestionCardProps> = ({ question }) => {
  const { upvote } = useVote(question.id);
  const swipeHandlers = useSwipeGesture(
    undefined,           // onSwipeLeft
    () => upvote()       // onSwipeRight = upvote
  );

  return (
    <div
      className="md:hidden"  // Only on mobile
      {...swipeHandlers}
    >
      {/* Card content */}
    </div>
  );
};
```

#### 4.5 Progressive Enhancement for Larger Screens

Add desktop-specific enhancements:

```tsx
// ContestPage.tsx - Enhanced desktop layout
<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
  {/* Main content - 2 columns on desktop */}
  <div className="lg:col-span-2 space-y-8">
    {/* Candidates, Questions */}
  </div>

  {/* Sidebar - only visible on desktop */}
  <div className="hidden lg:block space-y-6">
    {/* Sticky sidebar */}
    <div className="sticky top-24 space-y-6">
      <QuickStats contest={contest} />
      <ActionButtons contest={contest} />
      <RelatedContests contestId={contest.id} />
    </div>
  </div>
</div>
```

---

## 5. Loading States

### YouTube & Reddit Approach

#### Skeleton Screens
Both platforms use **skeleton screens** (placeholder UI) instead of spinners:

- **YouTube:** Shows thumbnail, title, and metadata placeholders while loading video cards
- **Reddit:** Displays post card skeletons with shimmering animation
- **2026 Best Practice:** Skeleton screens reduce perceived loading time by providing clues for how the page will look

**Research Finding:** Skeleton screens are indeterminate and are the new norm for full-page loading situations. For anything that takes less than 1 second, it's distracting to use a looped animation.

#### Progressive Loading
- **YouTube:** Loads visible content first (above-the-fold), lazy loads rest
- **Reddit:** Infinite scroll with progressive loading and skeleton screens
- **Feedback:** "Loading more..." text or spinner at bottom of feed

### Current CivicQ Implementation

```tsx
// LoadingSpinner.tsx - Simple spinner
<div className="flex flex-col items-center justify-center p-8">
  <div className={`animate-spin rounded-full border-b-2 border-civic-blue ${sizeClasses[size]}`}></div>
  {message && <p className="mt-4 text-gray-600 text-sm">{message}</p>}
</div>

// Usage in pages
{isLoading && <LoadingSpinner size="lg" message="Loading your ballot..." />}
```

**Status:** Basic spinner implementation. Works but not optimal for perceived performance.

### Recommendations for CivicQ

#### 5.1 Implement Skeleton Screens

Create skeleton components for different content types:

```tsx
// SkeletonCard.tsx
const SkeletonCard: React.FC = () => (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
    <div className="flex items-start space-x-4">
      {/* Vote skeleton */}
      <div className="flex flex-col items-center space-y-2">
        <div className="w-8 h-8 bg-gray-200 rounded"></div>
        <div className="w-8 h-4 bg-gray-200 rounded"></div>
        <div className="w-8 h-8 bg-gray-200 rounded"></div>
      </div>

      {/* Content skeleton */}
      <div className="flex-1 space-y-3">
        {/* Title */}
        <div className="h-6 bg-gray-200 rounded w-3/4"></div>
        <div className="h-6 bg-gray-200 rounded w-1/2"></div>

        {/* Context */}
        <div className="h-4 bg-gray-100 rounded w-full"></div>
        <div className="h-4 bg-gray-100 rounded w-5/6"></div>

        {/* Tags */}
        <div className="flex space-x-2">
          <div className="h-6 w-16 bg-gray-200 rounded-full"></div>
          <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
          <div className="h-6 w-14 bg-gray-200 rounded-full"></div>
        </div>

        {/* Metadata */}
        <div className="flex space-x-4">
          <div className="h-4 w-16 bg-gray-200 rounded"></div>
          <div className="h-4 w-20 bg-gray-200 rounded"></div>
          <div className="h-4 w-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  </div>
);

// SkeletonList.tsx - Shows multiple skeleton cards
const SkeletonList: React.FC<{ count?: number }> = ({ count = 3 }) => (
  <div className="space-y-4">
    {Array.from({ length: count }).map((_, i) => (
      <SkeletonCard key={i} />
    ))}
  </div>
);
```

#### 5.2 Add Shimmer Animation

Enhance skeleton screens with shimmer effect (like YouTube):

```css
/* styles/animations.css */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton-shimmer {
  animation: shimmer 2s infinite linear;
  background: linear-gradient(
    90deg,
    #f0f0f0 0px,
    #f8f8f8 40px,
    #f0f0f0 80px
  );
  background-size: 1000px 100%;
}
```

```tsx
// Apply to skeleton elements
<div className="h-6 bg-gray-200 rounded w-3/4 skeleton-shimmer"></div>
```

#### 5.3 Progressive Content Loading

Load content in stages:

```tsx
// ContestPage.tsx - Progressive loading
const ContestPage: React.FC = () => {
  const { contestId } = useParams();
  const [loadStage, setLoadStage] = useState<'contest' | 'candidates' | 'questions' | 'complete'>('contest');

  const { data: contest, isLoading: contestLoading } = useContest(contestId, {
    onSuccess: () => setLoadStage('candidates')
  });

  const { data: candidates, isLoading: candidatesLoading } = useContestCandidates(contestId, {
    enabled: loadStage !== 'contest',
    onSuccess: () => setLoadStage('questions')
  });

  const { data: questions, isLoading: questionsLoading } = useContestQuestions(contestId, {
    enabled: loadStage === 'questions' || loadStage === 'complete',
    onSuccess: () => setLoadStage('complete')
  });

  return (
    <Layout>
      {/* Contest header - loads first */}
      {contestLoading ? (
        <SkeletonContestHeader />
      ) : (
        <ContestHeader contest={contest} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Candidates - loads second */}
          <section>
            <h2 className="text-2xl font-bold mb-6">Candidates</h2>
            {candidatesLoading ? (
              <SkeletonList count={3} />
            ) : (
              candidates.map(c => <CandidateCard key={c.id} candidate={c} />)
            )}
          </section>

          {/* Questions - loads third */}
          <section>
            <h2 className="text-2xl font-bold mb-6">Questions</h2>
            {questionsLoading ? (
              <SkeletonList count={5} />
            ) : (
              questions.map(q => <QuestionCard key={q.id} question={q} />)
            )}
          </section>
        </div>

        {/* Sidebar loads last */}
        <div className="hidden lg:block">
          {loadStage === 'complete' ? (
            <ContestSidebar contest={contest} />
          ) : (
            <SkeletonSidebar />
          )}
        </div>
      </div>
    </Layout>
  );
};
```

#### 5.4 Optimistic UI Updates

Update UI immediately on user actions, then sync with server:

```tsx
// Optimistic voting
const useVote = (questionId: number) => {
  const queryClient = useQueryClient();

  const upvote = useMutation({
    mutationFn: () => api.upvoteQuestion(questionId),

    // Optimistic update
    onMutate: async () => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries(['question', questionId]);

      // Snapshot previous value
      const previousQuestion = queryClient.getQueryData(['question', questionId]);

      // Optimistically update
      queryClient.setQueryData(['question', questionId], (old: Question) => ({
        ...old,
        upvotes: old.upvotes + 1,
        userVote: 1,
      }));

      return { previousQuestion };
    },

    // Rollback on error
    onError: (err, variables, context) => {
      if (context?.previousQuestion) {
        queryClient.setQueryData(['question', questionId], context.previousQuestion);
      }
      toast.error('Failed to vote. Please try again.');
    },

    // Refetch on success or error
    onSettled: () => {
      queryClient.invalidateQueries(['question', questionId]);
    },
  });

  return { upvote };
};
```

#### 5.5 Empty States

Create helpful empty states (not just "No data"):

```tsx
// EmptyState.tsx
interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action
}) => (
  <div className="bg-gray-50 rounded-lg p-12 text-center">
    <div className="flex justify-center mb-4">
      <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-gray-400">
        {icon}
      </div>
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
    {action && (
      <button
        onClick={action.onClick}
        className="px-6 py-3 bg-civic-blue text-white rounded-lg hover:bg-blue-700
                   transition-colors font-medium"
      >
        {action.label}
      </button>
    )}
  </div>
);

// Usage examples
// No questions yet
<EmptyState
  icon={<QuestionMarkCircleIcon className="w-8 h-8" />}
  title="No questions yet"
  description="Be the first to ask a question about this contest. Help your community get the answers that matter."
  action={{
    label: 'Ask a Question',
    onClick: () => setShowQuestionForm(true)
  }}
/>

// No candidates yet
<EmptyState
  icon={<UsersIcon className="w-8 h-8" />}
  title="No candidates registered"
  description="Candidates haven't registered for this contest yet. Check back closer to the election date."
/>

// No answers yet
<EmptyState
  icon={<VideoIcon className="w-8 h-8" />}
  title="No answers yet"
  description="This question hasn't been answered by candidates yet. It may be answered as we get closer to the election."
/>
```

---

## 6. Error Handling

### YouTube & Reddit Approach

#### Error Types & Patterns
Both platforms handle errors gracefully with context-aware messaging:

- **Network Errors:** "Something went wrong. Try again." with retry button
- **Not Found (404):** Friendly "This video isn't available" or "Sorry, there aren't any communities on Reddit with that name"
- **Permissions:** Clear explanation with action ("Sign in to continue")
- **Rate Limiting:** "You're doing that too much. Try again in X minutes."

#### Toast Notifications
**Research Finding:** Toast notifications are ideal for confirming completed actions and brief error messages. However, they have critical limitations for errors:
- Users often don't get a chance to fully read before auto-dismiss
- Positioned far from the erroneous input
- Accessibility issues for users needing more time

**Best Practices:**
- Don't use dismissing toasts for critical or emergency messages
- Tie error messages to the user—what action failed and why
- Provide actionable next steps

### Current CivicQ Implementation

```tsx
// ErrorMessage.tsx - Inline error component
<div className="bg-red-50 border border-red-200 rounded-lg p-6">
  <div className="flex items-start">
    <div className="flex-shrink-0">
      <svg className="h-6 w-6 text-red-400">...</svg>
    </div>
    <div className="ml-3 flex-1">
      <h3 className="text-sm font-medium text-red-800">Error</h3>
      <p className="mt-1 text-sm text-red-700">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-3 text-sm font-medium text-red-800...">
          Try again
        </button>
      )}
    </div>
  </div>
</div>
```

**Status:** Good foundation for inline errors, but missing toast notifications and contextual error handling.

### Recommendations for CivicQ

#### 6.1 Implement Toast Notification System

Use a library like `react-hot-toast` or `sonner` for non-critical notifications:

```bash
npm install sonner
```

```tsx
// App.tsx - Add toast provider
import { Toaster } from 'sonner';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          {/* Routes */}
        </BrowserRouter>

        {/* Toast container */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#333',
              border: '1px solid #e5e7eb',
            },
            className: 'toast-custom',
          }}
        />
      </AuthProvider>
    </QueryClientProvider>
  );
}
```

```tsx
// Usage throughout app
import { toast } from 'sonner';

// Success
const handleVote = async () => {
  try {
    await upvote();
    toast.success('Vote recorded!', {
      description: 'Your vote has been counted.',
      icon: '✓',
    });
  } catch (error) {
    toast.error('Failed to vote', {
      description: 'Please try again or check your connection.',
      action: {
        label: 'Retry',
        onClick: () => handleVote(),
      },
    });
  }
};

// Info
toast.info('Question submitted for review', {
  description: 'You'll be notified once it's approved.',
});

// Warning
toast.warning('You've reached the daily limit', {
  description: 'You can submit 5 more questions tomorrow.',
});
```

#### 6.2 Contextual Error Handling

Display errors near their context, not just globally:

```tsx
// Form validation errors
const QuestionForm: React.FC = () => {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate
    const newErrors: Record<string, string> = {};
    if (!questionText.trim()) {
      newErrors.questionText = 'Question is required';
    }
    if (questionText.length < 10) {
      newErrors.questionText = 'Question must be at least 10 characters';
    }
    if (questionText.length > 500) {
      newErrors.questionText = 'Question must be less than 500 characters';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Submit...
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
          Your Question
        </label>
        <textarea
          id="question"
          value={questionText}
          onChange={(e) => {
            setQuestionText(e.target.value);
            // Clear error on change
            if (errors.questionText) {
              setErrors({ ...errors, questionText: '' });
            }
          }}
          className={`
            w-full px-4 py-3 border rounded-lg
            focus:ring-2 focus:ring-civic-blue focus:border-transparent
            ${errors.questionText
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300'}
          `}
          rows={4}
          aria-invalid={!!errors.questionText}
          aria-describedby={errors.questionText ? 'question-error' : undefined}
        />

        {/* Error message directly below input */}
        {errors.questionText && (
          <p
            id="question-error"
            className="mt-2 text-sm text-red-600 flex items-start"
            role="alert"
          >
            <ExclamationCircleIcon className="w-5 h-5 mr-1 flex-shrink-0" />
            {errors.questionText}
          </p>
        )}

        {/* Character count */}
        <p className="mt-2 text-sm text-gray-500 text-right">
          {questionText.length} / 500 characters
        </p>
      </div>

      <button type="submit" className="...">
        Submit Question
      </button>
    </form>
  );
};
```

#### 6.3 Network Error Recovery

Handle network issues gracefully:

```tsx
// ErrorBoundary.tsx enhancement for network errors
const NetworkErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({
  error,
  resetErrorBoundary,
}) => {
  const isOnline = useOnlineStatus();
  const [retryCount, setRetryCount] = useState(0);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    resetErrorBoundary();
  };

  // Auto-retry when coming back online
  useEffect(() => {
    if (isOnline && retryCount < 3) {
      const timer = setTimeout(() => {
        handleRetry();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [isOnline]);

  if (!isOnline) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <WifiOffIcon className="w-8 h-8 text-yellow-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Internet Connection</h2>
          <p className="text-gray-600 mb-6">
            It looks like you're offline. Check your connection and we'll automatically retry.
          </p>
          <div className="flex items-center justify-center text-sm text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-civic-blue mr-2"></div>
            Waiting for connection...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <ExclamationCircleIcon className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Something Went Wrong</h2>
        <p className="text-gray-600 mb-6">
          We're having trouble loading this page. This might be a temporary issue.
        </p>

        {retryCount > 0 && (
          <p className="text-sm text-gray-500 mb-4">
            Retry attempt {retryCount} of 3
          </p>
        )}

        <div className="space-y-3">
          <button
            onClick={handleRetry}
            className="w-full px-6 py-3 bg-civic-blue text-white rounded-lg
                       hover:bg-blue-700 transition-colors font-medium"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.href = '/'}
            className="w-full px-6 py-3 border border-gray-300 text-gray-700 rounded-lg
                       hover:bg-gray-50 transition-colors font-medium"
          >
            Go to Home
          </button>
        </div>

        {error.message && (
          <details className="mt-6 text-left">
            <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
              Technical details
            </summary>
            <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto">
              {error.message}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};
```

#### 6.4 API Error Handling with Context

Provide specific, actionable error messages:

```tsx
// api.ts - Enhanced error handling
class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public userMessage: string,
    public actionable?: boolean,
    public retryable?: boolean
  ) {
    super(message);
    this.name = 'APIError';
  }
}

const handleAPIError = (error: any): never => {
  if (error.response) {
    const { status, data } = error.response;

    switch (status) {
      case 400:
        throw new APIError(
          data.detail || 'Bad request',
          400,
          'There was a problem with your request. Please check your input and try again.',
          true,
          false
        );

      case 401:
        throw new APIError(
          'Unauthorized',
          401,
          'Your session has expired. Please log in again to continue.',
          true,
          false
        );

      case 403:
        throw new APIError(
          'Forbidden',
          403,
          "You don't have permission to perform this action.",
          false,
          false
        );

      case 404:
        throw new APIError(
          'Not found',
          404,
          "We couldn't find what you're looking for. It may have been removed or doesn't exist.",
          false,
          false
        );

      case 429:
        const retryAfter = error.response.headers['retry-after'] || 60;
        throw new APIError(
          'Rate limit exceeded',
          429,
          `You're doing that too much. Please try again in ${retryAfter} seconds.`,
          false,
          true
        );

      case 500:
      case 502:
      case 503:
      case 504:
        throw new APIError(
          'Server error',
          status,
          "We're experiencing technical difficulties. Please try again in a moment.",
          true,
          true
        );

      default:
        throw new APIError(
          `HTTP ${status}`,
          status,
          'Something went wrong. Please try again.',
          true,
          true
        );
    }
  }

  // Network error
  if (error.request) {
    throw new APIError(
      'Network error',
      0,
      'Unable to connect to CivicQ. Please check your internet connection and try again.',
      true,
      true
    );
  }

  // Something else
  throw new APIError(
    error.message,
    0,
    'An unexpected error occurred. Please try again.',
    true,
    true
  );
};

// Usage in hooks
const useCreateQuestion = () => {
  return useMutation({
    mutationFn: (data: CreateQuestionInput) => api.createQuestion(data),
    onError: (error: APIError) => {
      // Show appropriate error message
      if (error.statusCode === 401) {
        toast.error(error.userMessage, {
          action: {
            label: 'Log In',
            onClick: () => navigate('/login'),
          },
        });
      } else if (error.retryable) {
        toast.error(error.userMessage, {
          action: {
            label: 'Retry',
            onClick: () => mutate(data),
          },
        });
      } else {
        toast.error(error.userMessage);
      }
    },
  });
};
```

#### 6.5 404 Page

Create a helpful, friendly 404 page (like YouTube's):

```tsx
// NotFoundPage.tsx
const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthContext();

  return (
    <Layout>
      <div className="min-h-[60vh] flex items-center justify-center p-4">
        <div className="text-center max-w-lg">
          {/* Fun illustration or icon */}
          <div className="mb-8">
            <div className="text-9xl font-bold text-gray-200">404</div>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Page Not Found
          </h1>

          <p className="text-lg text-gray-600 mb-8">
            This page doesn't exist or may have been moved. Let's get you back on track.
          </p>

          <div className="space-y-3">
            <button
              onClick={() => navigate(-1)}
              className="w-full sm:w-auto px-6 py-3 bg-civic-blue text-white rounded-lg
                         hover:bg-blue-700 transition-colors font-medium"
            >
              Go Back
            </button>

            <Link
              to={user ? '/ballot' : '/'}
              className="block w-full sm:w-auto sm:inline-block sm:ml-3 px-6 py-3
                         border border-gray-300 text-gray-700 rounded-lg
                         hover:bg-gray-50 transition-colors font-medium"
            >
              {user ? 'Go to My Ballot' : 'Go to Home'}
            </Link>
          </div>

          {/* Helpful links */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-4">Looking for something specific?</p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link to="/ballot" className="text-civic-blue hover:underline">
                My Ballot
              </Link>
              <Link to="/questions" className="text-civic-blue hover:underline">
                Questions
              </Link>
              <Link to="/candidates" className="text-civic-blue hover:underline">
                Candidates
              </Link>
              <Link to="/help" className="text-civic-blue hover:underline">
                Help Center
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
```

---

## 7. Additional Best Practices

### 7.1 Search Functionality

Like YouTube's prominent search bar:

```tsx
// SearchBar.tsx
const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResults | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery.length >= 3) {
      searchContent(debouncedQuery);
    } else {
      setResults(null);
    }
  }, [debouncedQuery]);

  const searchContent = async (q: string) => {
    setIsSearching(true);
    try {
      const data = await api.search(q);
      setResults(data);
    } catch (error) {
      toast.error('Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="relative flex-1 max-w-2xl">
      <div className="relative">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search questions, candidates, contests..."
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg
                     focus:ring-2 focus:ring-civic-blue focus:border-transparent"
          aria-label="Search"
        />
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />

        {isSearching && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-civic-blue"></div>
          </div>
        )}
      </div>

      {/* Search results dropdown */}
      {results && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg
                        border border-gray-200 max-h-96 overflow-auto z-50">
          {results.questions.length > 0 && (
            <div className="p-2">
              <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Questions
              </h3>
              {results.questions.slice(0, 3).map(q => (
                <Link
                  key={q.id}
                  to={`/question/${q.id}`}
                  className="block px-3 py-2 hover:bg-gray-50 rounded"
                  onClick={() => setQuery('')}
                >
                  <p className="text-sm font-medium text-gray-900 line-clamp-1">
                    {q.question_text}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {q.upvotes - q.downvotes} votes • {q.video_answers?.length || 0} answers
                  </p>
                </Link>
              ))}
            </div>
          )}

          {results.candidates.length > 0 && (
            <div className="p-2 border-t border-gray-100">
              <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Candidates
              </h3>
              {results.candidates.slice(0, 3).map(c => (
                <Link
                  key={c.id}
                  to={`/candidate/${c.id}`}
                  className="block px-3 py-2 hover:bg-gray-50 rounded"
                  onClick={() => setQuery('')}
                >
                  <p className="text-sm font-medium text-gray-900">{c.name}</p>
                  <p className="text-xs text-gray-500 mt-1">{c.office}</p>
                </Link>
              ))}
            </div>
          )}

          {results.contests.length > 0 && (
            <div className="p-2 border-t border-gray-100">
              <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Contests
              </h3>
              {results.contests.slice(0, 3).map(c => (
                <Link
                  key={c.id}
                  to={`/contest/${c.id}`}
                  className="block px-3 py-2 hover:bg-gray-50 rounded"
                  onClick={() => setQuery('')}
                >
                  <p className="text-sm font-medium text-gray-900">{c.title}</p>
                </Link>
              ))}
            </div>
          )}

          {results.total === 0 && (
            <div className="p-8 text-center text-gray-500">
              <p className="text-sm">No results found for "{query}"</p>
            </div>
          )}

          {results.total > 9 && (
            <div className="p-2 border-t border-gray-100">
              <Link
                to={`/search?q=${encodeURIComponent(query)}`}
                className="block px-3 py-2 text-center text-sm font-medium text-civic-blue
                           hover:bg-gray-50 rounded"
                onClick={() => setQuery('')}
              >
                See all {results.total} results
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

### 7.2 Infinite Scroll vs. Pagination

**Research Finding:** YouTube and Reddit use infinite scroll for their main feeds. Infinite scroll works best for continuous browsing and engagement, but pagination is better when users need to find specific items.

**Recommendation for CivicQ:**

- **Use infinite scroll for:** Question feeds, candidate answer lists
- **Use pagination for:** Search results, admin interfaces, archival views

```tsx
// InfiniteScroll implementation for questions
const QuestionFeed: React.FC = () => {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['questions', contestId],
    queryFn: ({ pageParam = 1 }) => api.getQuestions(contestId, pageParam),
    getNextPageParam: (lastPage) => lastPage.nextPage,
  });

  const { ref, inView } = useInView({
    threshold: 0,
  });

  // Fetch next page when sentinel comes into view
  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage]);

  return (
    <div className="space-y-4">
      {data?.pages.map((page, i) => (
        <React.Fragment key={i}>
          {page.items.map((question) => (
            <QuestionCard key={question.id} question={question} />
          ))}
        </React.Fragment>
      ))}

      {/* Sentinel element */}
      {hasNextPage && (
        <div ref={ref} className="py-8 text-center">
          {isFetchingNextPage ? (
            <LoadingSpinner size="sm" message="Loading more questions..." />
          ) : (
            <button
              onClick={() => fetchNextPage()}
              className="text-civic-blue hover:underline"
            >
              Load more
            </button>
          )}
        </div>
      )}

      {!hasNextPage && data && data.pages[0].items.length > 0 && (
        <div className="py-8 text-center text-gray-500 text-sm">
          You've reached the end
        </div>
      )}
    </div>
  );
};
```

### 7.3 Video Player Best Practices (YouTube-inspired)

For CivicQ's candidate answer videos:

```tsx
// VideoPlayer.tsx enhancements
const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, answer }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(1);
  const [playbackRate, setPlaybackRate] = useState(1);
  const videoRef = useRef<HTMLVideoElement>(null);

  return (
    <div className="relative bg-black rounded-lg overflow-hidden group">
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full"
        onClick={() => setIsPlaying(!isPlaying)}
        onTimeUpdate={(e) => {
          const video = e.currentTarget;
          setProgress((video.currentTime / video.duration) * 100);
        }}
      />

      {/* Custom controls - shown on hover */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent
                      p-4 opacity-0 group-hover:opacity-100 transition-opacity">
        {/* Progress bar */}
        <div className="mb-3">
          <input
            type="range"
            min="0"
            max="100"
            value={progress}
            onChange={(e) => {
              const video = videoRef.current;
              if (video) {
                video.currentTime = (parseFloat(e.target.value) / 100) * video.duration;
              }
            }}
            className="w-full h-1 bg-white/30 rounded-full appearance-none
                       [&::-webkit-slider-thumb]:appearance-none
                       [&::-webkit-slider-thumb]:w-3
                       [&::-webkit-slider-thumb]:h-3
                       [&::-webkit-slider-thumb]:rounded-full
                       [&::-webkit-slider-thumb]:bg-civic-blue"
          />
        </div>

        <div className="flex items-center justify-between text-white">
          <div className="flex items-center space-x-3">
            {/* Play/Pause */}
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="hover:bg-white/20 p-2 rounded transition-colors"
            >
              {isPlaying ? <PauseIcon className="w-6 h-6" /> : <PlayIcon className="w-6 h-6" />}
            </button>

            {/* Volume */}
            <div className="flex items-center space-x-2">
              <button onClick={() => setVolume(volume === 0 ? 1 : 0)}>
                {volume === 0 ? (
                  <SpeakerXMarkIcon className="w-5 h-5" />
                ) : (
                  <SpeakerWaveIcon className="w-5 h-5" />
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={(e) => {
                  const vol = parseFloat(e.target.value);
                  setVolume(vol);
                  if (videoRef.current) videoRef.current.volume = vol;
                }}
                className="w-20"
              />
            </div>

            {/* Timestamp */}
            <span className="text-sm">
              {formatTime(videoRef.current?.currentTime || 0)} / {formatTime(videoRef.current?.duration || 0)}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {/* Playback speed */}
            <select
              value={playbackRate}
              onChange={(e) => {
                const rate = parseFloat(e.target.value);
                setPlaybackRate(rate);
                if (videoRef.current) videoRef.current.playbackRate = rate;
              }}
              className="bg-white/20 text-white text-sm rounded px-2 py-1"
            >
              <option value="0.5">0.5x</option>
              <option value="0.75">0.75x</option>
              <option value="1">Normal</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
            </select>

            {/* Captions */}
            <button className="hover:bg-white/20 p-2 rounded transition-colors">
              <CaptionsIcon className="w-5 h-5" />
            </button>

            {/* Fullscreen */}
            <button
              onClick={() => videoRef.current?.requestFullscreen()}
              className="hover:bg-white/20 p-2 rounded transition-colors"
            >
              <ArrowsPointingOutIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Metadata overlay */}
      <div className="absolute top-4 left-4 right-4">
        <div className="flex items-start justify-between">
          <div className="bg-black/60 backdrop-blur-sm rounded-lg px-3 py-2">
            <p className="text-white text-sm font-medium">{answer.candidate_name}</p>
            <p className="text-white/80 text-xs">{answer.office}</p>
          </div>

          {answer.verified && (
            <div className="bg-green-600/90 backdrop-blur-sm rounded-lg px-3 py-2
                            flex items-center text-white text-sm">
              <CheckBadgeIcon className="w-4 h-4 mr-1" />
              Verified
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
```

### 7.4 Accessibility Improvements

Ensure CivicQ is accessible to all users:

```tsx
// Add skip link for keyboard navigation
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4
             focus:z-50 focus:px-4 focus:py-2 focus:bg-civic-blue focus:text-white
             focus:rounded-lg"
>
  Skip to main content
</a>

// Proper heading hierarchy
<h1>Contest Title</h1>
<h2>Candidates</h2>
<h3>Candidate Name</h3>

// ARIA labels for icon-only buttons
<button aria-label="Upvote this question">
  <ArrowUpIcon />
</button>

// Focus management in modals
useEffect(() => {
  if (isOpen) {
    const firstFocusable = modalRef.current?.querySelector('button, [href], input, select, textarea');
    firstFocusable?.focus();
  }
}, [isOpen]);

// Keyboard navigation for custom components
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  Click me
</div>

// Screen reader announcements for dynamic content
const [announcement, setAnnouncement] = useState('');

const handleVote = async () => {
  await upvote();
  setAnnouncement('Vote recorded');
};

<div role="status" aria-live="polite" className="sr-only">
  {announcement}
</div>
```

---

## Implementation Priority

### Phase 1: Foundation (Week 1-2)
1. **Sticky Navigation** with smart scroll behavior
2. **Toast Notification System** for feedback
3. **Enhanced Error Handling** with contextual messages
4. **Skeleton Screens** for loading states

### Phase 2: Engagement (Week 3-4)
5. **Improved Vote Button** with animations and count display
6. **Mobile Bottom Navigation**
7. **Search Functionality**
8. **Empty States** for all scenarios

### Phase 3: Polish (Week 5-6)
9. **Infinite Scroll** for question feeds
10. **Progressive Content Loading**
11. **Enhanced Video Player**
12. **Filter and Sort Controls**

### Phase 4: Advanced (Week 7-8)
13. **Follow/Bookmark Features**
14. **User Progress Tracking**
15. **View Mode Toggle** (grid/list)
16. **Advanced Accessibility** improvements

---

## Metrics to Track

After implementing these improvements, track:

1. **Engagement Metrics:**
   - Average time on page
   - Questions submitted per user
   - Votes cast per session
   - Video completion rate

2. **Performance Metrics:**
   - Perceived load time (First Contentful Paint)
   - Time to Interactive
   - Largest Contentful Paint

3. **User Satisfaction:**
   - Error recovery rate
   - Session abandonment rate
   - Return user rate

4. **Accessibility:**
   - Keyboard navigation success rate
   - Screen reader compatibility
   - WCAG compliance score

---

## Sources

This document is based on research from the following sources:

### Navigation & Headers
- [Designing Sticky Menus: UX Guidelines — Smashing Magazine](https://www.smashingmagazine.com/2023/05/sticky-menus-ux-guidelines/)
- [What Is a Sticky Header? Guide (2026)](https://www.parallelhq.com/blog/what-sticky-header)
- [Mobile Navigation Patterns That Work in 2026 – Phone Simulator](https://phone-simulator.com/blog/mobile-navigation-patterns-in-2026)
- [Sticky Headers: 5 Ways to Make Them Better - NN/G](https://www.nngroup.com/articles/sticky-headers/)
- [Best UX Practices for Sidebar Menu Design in 2025](https://uiuxdesigntrends.com/best-ux-practices-for-sidebar-menu-in-2025/)

### Content Organization
- [Card Sorting: The Ultimate Guide for 2026 | IxDF](https://www.interaction-design.org/literature/article/the-pros-and-cons-of-card-sorting-in-ux-research)
- [How Card-Based Layouts Shape Modern UX | Design Shack](https://designshack.net/articles/ux-design/card-layouts-modern-ux/)
- [Vote To Promote design pattern](https://ui-patterns.com/patterns/VoteToPromote)
- [12 UI/UX Design Trends That Will Dominate 2026 (Data-Backed)](https://www.index.dev/blog/ui-ux-design-trends)

### Mobile Responsiveness
- [Responsive Web Design in 2026: Trends and Best Practices - Keel Info Solution](https://www.keelis.com/blog/responsive-web-design-in-2026:-trends-and-best-practices)
- [Responsive Design: Best Practices | IxDF](https://www.interaction-design.org/literature/article/responsive-design-let-the-device-do-the-work)
- [Mobile Navigation Design: 6 Patterns That Work in 2026](https://phone-simulator.com/blog/mobile-navigation-patterns-in-2026)
- [Responsive Design Best Practices: The Complete 2026 Guide | PxlPeak](https://pxlpeak.com/blog/web-design/responsive-design-best-practices)

### Loading States
- [Skeleton Screens 101 - NN/G](https://www.nngroup.com/articles/skeleton-screens/)
- [Skeleton loading screen design — How to improve perceived performance - LogRocket Blog](https://blog.logrocket.com/ux-design/skeleton-loading-screen-design/)
- [Effective Strategies for Empty State Design - Aufait UX](https://www.aufaitux.com/blog/empty-state-design/)
- [When to use loaders & empty states (and when not to) | UX Collective](https://uxdesign.cc/when-to-use-loaders-empty-states-ebd23cecc7d6)

### Error Handling
- [Error Message UX, Handling & Feedback - Pencil & Paper](https://www.pencilandpaper.io/articles/ux-pattern-analysis-error-feedback)
- [What is a toast notification? Best practices for UX - LogRocket Blog](https://blog.logrocket.com/ux-design/toast-notifications/)
- [Toast UI Design: Best practices | Mobbin](https://mobbin.com/glossary/toast)
- [Indicators, Validations, and Notifications - NN/G](https://www.nngroup.com/articles/indicators-validations-notifications/)

### Infinite Scroll & Pagination
- [Infinite Scrolling: When to Use It, When to Avoid It - NN/G](https://www.nngroup.com/articles/infinite-scrolling-tips/)
- [Infinite Scroll vs Pagination: How to Balance UX and SEO](https://ninjatables.com/infinite-scroll-vs-pagination/)
- [UX: Infinite Scrolling vs. Pagination | UX Planet](https://uxplanet.org/ux-infinite-scrolling-vs-pagination-1030d29376f1)

---

**Last Updated:** 2026-02-14
**Document Maintainer:** CivicQ Development Team
**Next Review:** 2026-03-14
