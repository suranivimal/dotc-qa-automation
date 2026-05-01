# Travel & Dating Social Platform - Project Requirements

---

## Table of Contents
1. [Key Concepts](#key-concepts)
2. [Mobile Application (React Native)](#mobile-application-react-native)
3. [Admin Panel](#admin-panel)
4. [Backend](#backend)
5. [Database Design](#database-design)
6. [Technology Stack](#technology-stack)
7. [Project Phases](#project-phases)

---

## Key Concepts

### Plan (Detailed Plan / Public Event)
A structured, detailed travel program created by a user (or group).

**Includes:**
- Activities
- Dates
- Location(s)
- Images
- Members
- Q&A
- Gallery

**Features:**
- Other travelers can join
- Members are visible

### Trip (Personal/Quick Entry)
A lightweight personal travel log or upcoming quick journey.

**Includes:**
- City name
- Start & end date
- Optional note

**Features:**
- Not joinable
- Only for user's dashboard

---

## Mobile Application (React Native)

### 1. User Accounts & Profiles
- **Authentication:**
  - Email login
  - Phone login
  - Social login

- **Profile Information:**
  - Profile photo
  - Bio
  - Location (city + country)
  - Interests
  - Optional identity tags (culture, language, values)

- **Controls:**
  - Privacy settings
  - Visibility controls

### 2. Discovery, Matching & Maps
- **Discovery Methods:**
  - By nearby location
  - By selected city
  - By travel destination

- **Filters:**
  - Age range
  - Interests
  - Travel status

- **Views:**
  - List view
  - Swipe discovery
  - Map view (approximate location only)

### 3. Community Groups & Feed
- **Group Types:**
  - Public groups
  - Private groups

- **Group Categories:**
  - By city
  - By destination
  - By interests

- **Features:**
  - Group feed (posts, photos, comments)
  - Moderation tools

### 4. Events & Meetups
- **Event Management:**
  - Create events
  - Join events
  - RSVP options (Going / Interested)

- **Features:**
  - Event chat
  - Map-based event locations
  - Public or group-only visibility

### 5. Messaging
- **Chat Types:**
  - 1:1 chat
  - Group chat

- **Features:**
  - Image sharing
  - Message requests
  - Block controls

### 6. Travel Mode
- **Functionality:**
  - Set travel destination and dates
  - Show "visiting this city" on profile
  - Discover locals and travelers in destination
  - Destination-specific feed

### 7. Travel Booking Integration (Tourseta)
- **Features:**
  - Browse Tourseta trips in-app
  - Book trips in-app
  - Secure checkout
  - Booked trips sync to user profile
  - Auto-join trip group chats & feeds
  - Booking updates via notifications

### 8. Travel & Business Marketplace
- **Marketplace Categories:**
  - Tours & experiences
  - Hotels / stays
  - Cafes
  - Coworking spaces
  - Local businesses

- **Business Listings Include:**
  - Description
  - Photos
  - Location
  - Link
  - Exclusive discounts or perks

- **Features:**
  - Affiliate / partner tagging (backend-ready)

### 9. Discounts & Deals
- **Deal Types:**
  - Trip-specific deals
  - Location-based deals
  - Partner-sponsored deals

- **Features:**
  - Promo codes
  - Special offers
  - "Deals for your trip" auto-surfaced

### 10. Dating Mode (Opt-In)
- **Configuration:**
  - Optional toggle (off by default)

- **Purpose Selection:**
  - Friendship
  - Networking
  - Open to dating

- **Features:**
  - Dating profiles visible only to dating-mode users

### 11. Travel-Based Dating & Singles Discovery
- **Matching Criteria:**
  - Current city
  - Travel destination
  - Overlapping travel dates

- **Features:**
  - Dating map (separate toggle)
  - Mutual match required before dating chat
  - Ability to pause or hide dating at any time

### 12. Core Safety & System Requirements
- **Safety Features:**
  - Block users
  - Report users
  - Report posts
  - Report messages

- **Admin Controls:**
  - Admin moderation dashboard

- **Notifications:**
  - Push notifications for chat
  - Push notifications for events
  - Push notifications for bookings
  - Push notifications for deals

- **Security:**
  - Secure authentication
  - Data privacy protection

---

## Admin Panel

### 2.1 Dashboard
- User count
- Plan count
- Trip count
- Reports overview

### 2.2 User Management
- View users
- Edit user information
- Verify users
- Upgrade/downgrade subscriptions

### 2.3 Reports & Moderation
- View reported users
- View reported trips
- View reported plans
- Suspend users
- Remove content

### 2.4 Subscription Management
- Manage premium plans
- Track payments
- Handle billing

---

## Backend

### 3.1 Authentication & User APIs
- Social login (Google, Apple)
- Profile create
- Profile update
- Subscription management

### 3.2 Plan APIs
- Create plans (CRUD)
- Update plans
- Delete plans
- Fetch trending plans
- Fetch popular plans
- Fetch new plans
- Join plan
- Leave plan
- Plan chat
- City-wise matching

### 3.3 Trip APIs
- Create trips (CRUD)
- Update trips
- Delete trips
- Fetch dashboard trips

### 3.4 Traveler APIs
- Nearby travelers (geo-query)
- Friend requests
- Friends list

### 3.5 Messaging APIs
- Direct chat
- Group chat
- Notifications

### 3.6 Admin APIs
- User management
- Plan management
- Trip management
- Reports handling

---

## Database Design

### Schema Entities
- **Users** - User accounts and credentials
- **Profiles** - Bio, social info, language, interests
- **Plans** - Travel plans with details, activities, city, members
- **Trips** - Personal travel logs
- **Messages** - Direct & group messages
- **Friends** - Friend relationships
- **Reports** - User/content reports
- **Subscriptions** - Premium plan subscriptions

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Mobile App** | React Native |
| **Admin Panel** | React |
| **Backend** | Node.js |
| **Database** | MySQL or PostgreSQL |
| **Authentication** | Social login (Google, Apple) |
| **Payments** | Apple Pay, Google Pay |
| **Notifications & Chat** | Real-time messaging (platform/service to be finalized) |
| **Hosting/Cloud** | To be finalized (AWS/GCP/Azure options) |

---

## Project Phases

| Phase | Description |
|-------|-------------|
| **1** | UI Design of Mobile App |
| **2** | Database Creation |
| **3** | API Development |
| **4** | Admin Development |
| **5** | Mobile App Development |
| **6** | QA |
| **7** | Deployment |

---

## Key Features Summary

### For Users
✅ Social discovery and matching  
✅ Travel planning and booking  
✅ Community groups and events  
✅ Real-time messaging  
✅ Dating mode (optional)  
✅ Marketplace for travel services  
✅ Exclusive deals and discounts  

### For Admins
✅ User management and verification  
✅ Content moderation  
✅ Subscription management  
✅ Reports handling  
✅ Platform analytics  

### For Platform
✅ Multi-platform deployment  
✅ Real-time notifications  
✅ Secure payment processing  
✅ Scalable architecture  
✅ Social login integration  

---

## Notes
- Dating mode is optional and off by default
- Location data is approximate for privacy
- All safety and moderation features are mandatory
- Backend architect should finalize hosting and real-time messaging provider

