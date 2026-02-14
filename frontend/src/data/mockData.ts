// Mock Data for CivicQ Demo Mode
import {
  Ballot,
  Contest,
  Candidate,
  Question,
  VideoAnswer,
  ContestType,
  CandidateStatus,
  QuestionStatus,
  AnswerStatus,
} from '../types';

// Sample Ballots for different cities
export const MOCK_BALLOTS: Ballot[] = [
  {
    id: 1,
    city_id: 'los-angeles-ca',
    city_name: 'Los Angeles',
    election_date: '2026-11-03',
    version: 1,
    is_published: true,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
  {
    id: 2,
    city_id: 'santa-monica-ca',
    city_name: 'Santa Monica',
    election_date: '2026-11-03',
    version: 1,
    is_published: true,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
  {
    id: 3,
    city_id: 'pasadena-ca',
    city_name: 'Pasadena',
    election_date: '2026-11-03',
    version: 1,
    is_published: true,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
];

// Sample Contests
export const MOCK_CONTESTS: Contest[] = [
  {
    id: 1,
    ballot_id: 1,
    type: 'race' as ContestType,
    title: 'Mayor of Los Angeles',
    jurisdiction: 'City of Los Angeles',
    office: 'Mayor',
    seat_count: 1,
    description:
      'The Mayor of Los Angeles is the chief executive officer of the city. The mayor presides over the city council and oversees all city departments.',
    display_order: 1,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
  {
    id: 2,
    ballot_id: 1,
    type: 'race' as ContestType,
    title: 'City Council District 5',
    jurisdiction: 'City of Los Angeles',
    office: 'City Council Member',
    seat_count: 1,
    description:
      'Represents District 5 on the Los Angeles City Council. Responsible for local legislation and constituent services.',
    display_order: 2,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
  {
    id: 3,
    ballot_id: 1,
    type: 'measure' as ContestType,
    title: 'Measure A: Affordable Housing Bond',
    jurisdiction: 'City of Los Angeles',
    description:
      'Shall the City of Los Angeles issue $1.2 billion in bonds to fund affordable housing development and homelessness prevention programs?',
    display_order: 3,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
  {
    id: 4,
    ballot_id: 2,
    type: 'race' as ContestType,
    title: 'Mayor of Santa Monica',
    jurisdiction: 'City of Santa Monica',
    office: 'Mayor',
    seat_count: 1,
    description:
      'The Mayor of Santa Monica presides over the city council and serves as the ceremonial head of the city.',
    display_order: 1,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
  },
];

// Sample Candidates
export const MOCK_CANDIDATES: Candidate[] = [
  // Mayor of LA candidates
  {
    id: 1,
    contest_id: 1,
    name: 'Karen Bass',
    email: 'karen@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Former U.S. Representative and community organizer with 30+ years of public service.',
      occupation: 'Current Mayor',
      education: 'Cal State Dominguez Hills',
    },
    photo_url: 'https://i.pravatar.cc/300?img=1',
    website: 'https://example.com/karen-bass',
    identity_verified: true,
    display_order: 1,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
  {
    id: 2,
    contest_id: 1,
    name: 'Rick Caruso',
    email: 'rick@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Real estate developer and business leader focused on economic development.',
      occupation: 'Real Estate Developer',
      education: 'Pepperdine University',
    },
    photo_url: 'https://i.pravatar.cc/300?img=12',
    website: 'https://example.com/rick-caruso',
    identity_verified: true,
    display_order: 2,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
  {
    id: 3,
    contest_id: 1,
    name: 'Kevin de León',
    email: 'kevin@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Los Angeles City Council Member and former California State Senate President.',
      occupation: 'City Council Member',
      education: 'UC Santa Barbara',
    },
    photo_url: 'https://i.pravatar.cc/300?img=13',
    website: 'https://example.com/kevin-deleon',
    identity_verified: true,
    display_order: 3,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
  // City Council District 5 candidates
  {
    id: 4,
    contest_id: 2,
    name: 'Katy Yaroslavsky',
    email: 'katy@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Environmental policy expert and community advocate.',
      occupation: 'Policy Advisor',
      education: 'UCLA',
    },
    photo_url: 'https://i.pravatar.cc/300?img=5',
    website: 'https://example.com/katy',
    identity_verified: true,
    display_order: 1,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
  {
    id: 5,
    contest_id: 2,
    name: 'Sam Yebri',
    email: 'sam@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Attorney and community leader focused on public safety and economic growth.',
      occupation: 'Attorney',
      education: 'USC Law',
    },
    photo_url: 'https://i.pravatar.cc/300?img=14',
    website: 'https://example.com/sam',
    identity_verified: true,
    display_order: 2,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
  // Santa Monica Mayor candidates
  {
    id: 6,
    contest_id: 4,
    name: 'Gleam Davis',
    email: 'gleam@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Former Santa Monica City Council member and education advocate.',
      occupation: 'City Council Member',
      education: 'Stanford University',
    },
    photo_url: 'https://i.pravatar.cc/300?img=10',
    website: 'https://example.com/gleam',
    identity_verified: true,
    display_order: 1,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
  {
    id: 7,
    contest_id: 4,
    name: 'Phil Brock',
    email: 'phil@example.com',
    status: 'active' as CandidateStatus,
    profile_fields: {
      bio: 'Business owner and community organizer focused on local economic development.',
      occupation: 'Business Owner',
      education: 'USC',
    },
    photo_url: 'https://i.pravatar.cc/300?img=15',
    website: 'https://example.com/phil',
    identity_verified: true,
    display_order: 2,
    created_at: '2026-01-20T00:00:00Z',
    updated_at: '2026-01-20T00:00:00Z',
  },
];

// Sample Questions
export const MOCK_QUESTIONS: Question[] = [
  {
    id: 1,
    contest_id: 1,
    question_text: 'What is your plan to address homelessness in Los Angeles?',
    issue_tags: ['homelessness', 'housing', 'social services'],
    status: 'approved' as QuestionStatus,
    context:
      'Los Angeles has over 40,000 unhoused residents. What specific policies and programs will you implement?',
    upvotes: 342,
    downvotes: 15,
    rank_score: 327,
    is_flagged: 0,
    created_at: '2026-02-01T00:00:00Z',
    updated_at: '2026-02-01T00:00:00Z',
  },
  {
    id: 2,
    contest_id: 1,
    question_text: 'How will you improve public transportation and reduce traffic congestion?',
    issue_tags: ['transportation', 'infrastructure', 'climate'],
    status: 'approved' as QuestionStatus,
    context:
      'Los Angeles traffic costs residents billions in lost productivity. What solutions do you propose?',
    upvotes: 289,
    downvotes: 8,
    rank_score: 281,
    is_flagged: 0,
    created_at: '2026-02-02T00:00:00Z',
    updated_at: '2026-02-02T00:00:00Z',
  },
  {
    id: 3,
    contest_id: 1,
    question_text: 'What are your priorities for public safety and police reform?',
    issue_tags: ['public safety', 'police reform', 'criminal justice'],
    status: 'approved' as QuestionStatus,
    upvotes: 256,
    downvotes: 42,
    rank_score: 214,
    is_flagged: 0,
    created_at: '2026-02-03T00:00:00Z',
    updated_at: '2026-02-03T00:00:00Z',
  },
  {
    id: 4,
    contest_id: 1,
    question_text: 'How will you address the affordable housing crisis?',
    issue_tags: ['housing', 'affordability', 'development'],
    status: 'approved' as QuestionStatus,
    context: 'Median rent in LA has increased 35% in the past 5 years.',
    upvotes: 198,
    downvotes: 12,
    rank_score: 186,
    is_flagged: 0,
    created_at: '2026-02-04T00:00:00Z',
    updated_at: '2026-02-04T00:00:00Z',
  },
  {
    id: 5,
    contest_id: 2,
    question_text: 'What is your vision for sustainable development in District 5?',
    issue_tags: ['environment', 'development', 'sustainability'],
    status: 'approved' as QuestionStatus,
    upvotes: 124,
    downvotes: 5,
    rank_score: 119,
    is_flagged: 0,
    created_at: '2026-02-05T00:00:00Z',
    updated_at: '2026-02-05T00:00:00Z',
  },
  {
    id: 6,
    contest_id: 2,
    question_text: 'How will you improve parks and recreation facilities in our district?',
    issue_tags: ['parks', 'recreation', 'quality of life'],
    status: 'approved' as QuestionStatus,
    upvotes: 98,
    downvotes: 3,
    rank_score: 95,
    is_flagged: 0,
    created_at: '2026-02-06T00:00:00Z',
    updated_at: '2026-02-06T00:00:00Z',
  },
  {
    id: 7,
    contest_id: 4,
    question_text: 'What is your plan to support small businesses in Santa Monica?',
    issue_tags: ['economy', 'small business', 'jobs'],
    status: 'approved' as QuestionStatus,
    upvotes: 156,
    downvotes: 8,
    rank_score: 148,
    is_flagged: 0,
    created_at: '2026-02-07T00:00:00Z',
    updated_at: '2026-02-07T00:00:00Z',
  },
];

// Sample Video Answers
export const MOCK_VIDEO_ANSWERS: VideoAnswer[] = [
  // Answers for Question 1 (Homelessness)
  {
    id: 1,
    candidate_id: 1,
    question_id: 1,
    video_asset_id: 'demo-video-1',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    duration: 185,
    transcript_text:
      'Thank you for this important question. Homelessness is the defining crisis of our time in Los Angeles. My comprehensive plan includes three key pillars: First, creating 15,000 new emergency shelter beds within the first year. Second, expanding mental health and substance abuse treatment programs. Third, implementing a Housing First model with wraparound services to ensure long-term stability.',
    status: 'published' as AnswerStatus,
    position_summary: 'Housing First approach with expanded services and shelter beds',
    rationale:
      'Evidence shows Housing First works. Cities like Houston have reduced homelessness by 60% using this model.',
    implementation_plan:
      'Partner with nonprofits and use state funding. Deploy mental health crisis teams citywide.',
    measurement_criteria:
      'Reduce unsheltered homelessness by 30% in first two years. Track housing placement rates monthly.',
    values_statement:
      'Everyone deserves dignity and a safe place to call home. This is a moral imperative.',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-10T00:00:00Z',
    updated_at: '2026-02-10T00:00:00Z',
  },
  {
    id: 2,
    candidate_id: 2,
    question_id: 1,
    video_asset_id: 'demo-video-2',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    duration: 165,
    transcript_text:
      'We need a business-minded approach to homelessness. I propose building tiny home villages on city-owned land, partnering with private developers to create affordable housing units, and implementing strict enforcement of anti-camping laws while providing genuine alternatives.',
    status: 'published' as AnswerStatus,
    position_summary: 'Public-private partnerships and interim housing solutions',
    rationale:
      'The private sector can build housing faster and more efficiently than government alone.',
    implementation_plan:
      'Identify 20 city-owned parcels for tiny homes. Create tax incentives for developers.',
    measurement_criteria: 'Build 5,000 tiny homes in year one. Clear encampments within 18 months.',
    values_statement: 'Compassion must be paired with accountability and practical solutions.',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-10T00:00:00Z',
    updated_at: '2026-02-10T00:00:00Z',
  },
  {
    id: 3,
    candidate_id: 3,
    question_id: 1,
    video_asset_id: 'demo-video-3',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
    duration: 172,
    transcript_text:
      'As someone who represents one of the most affected districts, I see this crisis every day. We need to declare a state of emergency, unlock state and federal funding, create a unified homelessness authority, and build permanent supportive housing at scale.',
    status: 'published' as AnswerStatus,
    position_summary: 'Emergency declaration with coordinated city-county response',
    rationale:
      'Current fragmented system wastes resources. We need unified command and control.',
    implementation_plan:
      'Create Office of Homelessness Czar reporting directly to Mayor. Streamline permitting.',
    measurement_criteria:
      'House 25,000 people in first year. Reduce street homelessness by 50% by 2028.',
    values_statement: 'Housing is a human right, and we must act with urgency and compassion.',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-10T00:00:00Z',
    updated_at: '2026-02-10T00:00:00Z',
  },
  // Answers for Question 2 (Transportation)
  {
    id: 4,
    candidate_id: 1,
    question_id: 2,
    video_asset_id: 'demo-video-4',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
    duration: 158,
    transcript_text:
      'We must invest heavily in public transit. I support expanding Metro lines, increasing bus frequency, creating dedicated bus lanes, and making transit free for students and seniors.',
    status: 'published' as AnswerStatus,
    position_summary: 'Expand Metro, increase bus service, and reduce fares',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-11T00:00:00Z',
    updated_at: '2026-02-11T00:00:00Z',
  },
  {
    id: 5,
    candidate_id: 2,
    question_id: 2,
    video_asset_id: 'demo-video-5',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    duration: 145,
    transcript_text:
      'Smart technology and infrastructure are key. Synchronize traffic lights with AI, expand ride-sharing lanes, invest in aerial transit like gondolas, and improve road maintenance.',
    status: 'published' as AnswerStatus,
    position_summary: 'Technology-driven solutions and infrastructure innovation',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-11T00:00:00Z',
    updated_at: '2026-02-11T00:00:00Z',
  },
  // Answers for Question 5 (District 5 Development)
  {
    id: 6,
    candidate_id: 4,
    question_id: 5,
    video_asset_id: 'demo-video-6',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
    duration: 168,
    transcript_text:
      'District 5 must lead on climate action. I support green building requirements, protecting open spaces, investing in EV infrastructure, and creating walkable neighborhoods.',
    status: 'published' as AnswerStatus,
    position_summary: 'Green building standards and sustainable urban planning',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-12T00:00:00Z',
    updated_at: '2026-02-12T00:00:00Z',
  },
  {
    id: 7,
    candidate_id: 5,
    question_id: 5,
    video_asset_id: 'demo-video-7',
    video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4',
    duration: 152,
    transcript_text:
      'We need balanced growth that preserves neighborhood character while creating housing opportunities. I support transit-oriented development, small-lot subdivisions, and ADU incentives.',
    status: 'published' as AnswerStatus,
    position_summary: 'Balanced growth with neighborhood preservation',
    is_open_question: false,
    has_correction: false,
    created_at: '2026-02-12T00:00:00Z',
    updated_at: '2026-02-12T00:00:00Z',
  },
];

// Helper functions to get mock data
export const getMockBallots = (params?: {
  city_id?: string;
  is_published?: boolean;
}): Ballot[] => {
  let ballots = [...MOCK_BALLOTS];

  if (params?.city_id) {
    ballots = ballots.filter((b) => b.city_id === params.city_id);
  }

  if (params?.is_published !== undefined) {
    ballots = ballots.filter((b) => b.is_published === params.is_published);
  }

  return ballots;
};

export const getMockBallotById = (id: number): Ballot | undefined => {
  const ballot = MOCK_BALLOTS.find((b) => b.id === id);
  if (ballot) {
    // Add contests to ballot
    const contests = MOCK_CONTESTS.filter((c) => c.ballot_id === id);
    return { ...ballot, contests };
  }
  return undefined;
};

export const getMockContestById = (id: number): Contest | undefined => {
  return MOCK_CONTESTS.find((c) => c.id === id);
};

export const getMockContestCandidates = (contestId: number): Candidate[] => {
  const candidates = MOCK_CANDIDATES.filter((c) => c.contest_id === contestId);
  // Add video answers to each candidate
  return candidates.map((candidate) => ({
    ...candidate,
    video_answers: MOCK_VIDEO_ANSWERS.filter((a) => a.candidate_id === candidate.id),
  }));
};

export const getMockContestQuestions = (
  contestId: number,
  params?: { status?: string; page?: number; page_size?: number }
) => {
  let questions = MOCK_QUESTIONS.filter((q) => q.contest_id === contestId);

  if (params?.status) {
    questions = questions.filter((q) => q.status === params.status);
  }

  // Sort by rank score
  questions.sort((a, b) => b.rank_score - a.rank_score);

  const page = params?.page || 1;
  const pageSize = params?.page_size || 50;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;

  return {
    items: questions.slice(start, end),
    total: questions.length,
    page,
    page_size: pageSize,
    total_pages: Math.ceil(questions.length / pageSize),
  };
};

export const getMockQuestionById = (id: number): Question | undefined => {
  const question = MOCK_QUESTIONS.find((q) => q.id === id);
  if (question) {
    // Add video answers
    return {
      ...question,
      video_answers: MOCK_VIDEO_ANSWERS.filter((a) => a.question_id === id),
    };
  }
  return undefined;
};

export const getMockQuestionVideoAnswers = (questionId: number): VideoAnswer[] => {
  return MOCK_VIDEO_ANSWERS.filter((a) => a.question_id === questionId).map((answer) => ({
    ...answer,
    candidate: MOCK_CANDIDATES.find((c) => c.id === answer.candidate_id),
  }));
};

export const getMockCandidateById = (id: number): Candidate | undefined => {
  const candidate = MOCK_CANDIDATES.find((c) => c.id === id);
  if (candidate) {
    return {
      ...candidate,
      video_answers: MOCK_VIDEO_ANSWERS.filter((a) => a.candidate_id === id),
    };
  }
  return undefined;
};

export const getMockCandidateVideoAnswers = (candidateId: number): VideoAnswer[] => {
  return MOCK_VIDEO_ANSWERS.filter((a) => a.candidate_id === candidateId).map((answer) => ({
    ...answer,
    question: MOCK_QUESTIONS.find((q) => q.id === answer.question_id),
  }));
};
