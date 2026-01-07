# Pricing Page to Stripe Products Alignment Plan

## Current State Analysis

### Frontend Implementation
- **Location**: `web/apps/labelstudio/src/pages/Billing/BillingPage.jsx`
- **Component**: `PricingTable.jsx` uses Stripe's embedded pricing table (`<stripe-pricing-table>`)
- **Configuration**: 
  - Pricing table ID comes from `/api/billing/stripe-config/` endpoint
  - Falls back to hardcoded default: `prctbl_1ShORfAaooP90eyYgWNjXf6b`
  - Publishable key also from API or hardcoded default
- **Current Flow**: 
  - Authenticated users see pricing table on `/billing` page
  - Uses Stripe Customer Session for better customer recognition
  - Pricing table is embedded from Stripe Dashboard configuration

### Backend Implementation
- **API Endpoint**: `/api/billing/pricing/` (`PricingTableAPI`)
  - Fetches active prices from dj-stripe: `Price.objects.filter(active=True)`
  - Returns price data including: id, product_id, product_name, amount, currency, interval, etc.
  - **Currently not used by frontend** - frontend uses embedded Stripe pricing table instead
- **Stripe Configuration**: 
  - `STRIPE_PRICING_TABLE_ID` environment variable
  - Pricing table configured in Stripe Dashboard
  - Products and prices managed in Stripe Dashboard

### Issues Identified
1. **Disconnect**: Backend API fetches prices from dj-stripe, but frontend uses embedded Stripe pricing table
2. **Hardcoded Fallbacks**: Default pricing table ID and publishable key in frontend code
3. **No Public Landing Page**: Pricing only visible to authenticated users on `/billing` page
4. **Manual Sync Required**: Pricing table in Stripe Dashboard must be manually kept in sync with products/prices

## Goals

1. **Single Source of Truth**: Stripe Products/Prices should be the authoritative source
2. **Dynamic Pricing Display**: Frontend should display pricing fetched from Stripe API
3. **Consistency**: Ensure pricing shown matches exactly what's in Stripe
4. **Flexibility**: Support both embedded pricing table and custom pricing display
5. **Public Access**: Consider public landing page with pricing (if needed)

## Implementation Plan

### Phase 1: Enhance Backend API (Foundation)

#### 1.1 Improve Pricing API Response
**File**: `label_studio/billing/api.py` - `PricingTableAPI`

**Changes**:
- Add product metadata extraction (features, limits, etc.)
- Include pricing table configuration data
- Add tier mapping (FREE, PLUS, PRO) based on product names
- Include usage limits from product metadata
- Add currency formatting helpers
- Return structured data for easy frontend consumption

**New Response Structure**:
```python
{
  "prices": [
    {
      "id": "price_xxx",
      "product_id": "prod_xxx",
      "product_name": "Plus Plan",
      "tier": "PLUS",
      "amount": 2900,
      "currency": "usd",
      "formatted_amount": "$29.00",
      "interval": "month",
      "interval_count": 1,
      "active": true,
      "description": "...",
      "features": [...],  # from product metadata
      "limits": {
        "max_projects": 10,
        "max_tasks": 50
      }
    }
  ],
  "grouped_by_tier": {
    "FREE": {...},
    "PLUS": {...},
    "PRO": {...}
  }
}
```

#### 1.2 Add Public Pricing Endpoint (Optional)
**File**: `label_studio/billing/api.py`

**New Endpoint**: `GET /api/billing/public-pricing/`
- No authentication required
- Returns active prices for public landing page
- Same structure as authenticated endpoint
- Excludes customer-specific data

#### 1.3 Add Pricing Validation Utility
**File**: `label_studio/billing/utils.py`

**New Function**: `validate_pricing_table_alignment()`
- Compares Stripe Pricing Table configuration with active products/prices
- Logs discrepancies
- Can be run as management command for monitoring

### Phase 2: Frontend Refactoring

#### 2.1 Create Custom Pricing Display Component
**File**: `web/apps/labelstudio/src/pages/Billing/CustomPricingTable.jsx`

**Features**:
- Fetches pricing from `/api/billing/pricing/` endpoint
- Displays pricing in custom UI matching design system
- Shows tier information, features, limits
- Handles loading and error states
- Supports both authenticated and public views

**Benefits**:
- Full control over pricing display
- Consistent with app design
- Can show additional information (usage limits, features)
- No dependency on Stripe's embedded component

#### 2.2 Update BillingPage Component
**File**: `web/apps/labelstudio/src/pages/Billing/BillingPage.jsx`

**Changes**:
- Add feature flag or setting to choose between:
  - Embedded Stripe pricing table (current)
  - Custom pricing display (new)
- Use custom component when enabled
- Maintain backward compatibility

#### 2.3 Remove Hardcoded Defaults
**File**: `web/apps/labelstudio/src/pages/Billing/PricingTable.jsx`

**Changes**:
- Remove hardcoded `defaultPricingTableId` and `defaultPublishableKey`
- Require these values from API or show error if missing
- Improve error handling for missing configuration

### Phase 3: Public Landing Page (If Needed)

#### 3.1 Create Public Pricing Page Component
**File**: `web/apps/labelstudio/src/pages/Pricing/PricingPage.jsx`

**Features**:
- Public-facing pricing page
- Fetches from `/api/billing/public-pricing/`
- No authentication required
- SEO-friendly
- Call-to-action buttons

#### 3.2 Add Route
**File**: `web/apps/labelstudio/src/routes/` or routing configuration

**Route**: `/pricing` (public)

### Phase 4: Sync & Monitoring

#### 4.1 Create Management Command
**File**: `label_studio/billing/management/commands/sync_pricing_table.py`

**Purpose**:
- Validates pricing table alignment
- Syncs product metadata to pricing table
- Reports discrepancies
- Can be run in CI/CD or scheduled job

#### 4.2 Add Monitoring
- Log pricing changes
- Alert on pricing table misalignment
- Track pricing API usage

### Phase 5: Documentation & Testing

#### 5.1 Update Documentation
- Document pricing structure
- Explain how to add/modify products in Stripe
- Provide examples of product metadata format
- Update API documentation

#### 5.2 Testing
- Unit tests for pricing API
- Integration tests for pricing display
- E2E tests for pricing flow
- Test pricing table sync validation

## Implementation Steps (Priority Order)

### Step 1: Enhance Backend API (High Priority)
1. Update `PricingTableAPI` to return richer data structure
2. Extract product metadata (features, limits)
3. Add tier mapping logic
4. Add currency formatting
5. Test API response

### Step 2: Create Custom Pricing Component (High Priority)
1. Create `CustomPricingTable.jsx` component
2. Fetch from pricing API
3. Design pricing cards/table UI
4. Add loading and error states
5. Test component

### Step 3: Update BillingPage (Medium Priority)
1. Add feature flag for pricing display mode
2. Integrate custom pricing component
3. Maintain backward compatibility
4. Test both modes

### Step 4: Remove Hardcoded Defaults (Medium Priority)
1. Remove hardcoded values from `PricingTable.jsx`
2. Improve error handling
3. Update tests

### Step 5: Public Landing Page (Low Priority - If Needed)
1. Create public pricing page component
2. Add public pricing API endpoint
3. Add route
4. Test public access

### Step 6: Sync & Monitoring (Low Priority)
1. Create management command
2. Add validation logic
3. Set up monitoring
4. Document process

## Technical Considerations

### Product Metadata Structure
Products in Stripe should have metadata like:
```json
{
  "tier": "PLUS",
  "max_projects": "10",
  "max_tasks": "50",
  "features": "feature1,feature2,feature3"
}
```

### Tier Mapping
- Product names should contain tier identifiers: "FREE", "PLUS", "PRO"
- Or use product metadata `tier` field
- Fallback to name parsing (current implementation)

### Currency Handling
- Support multiple currencies if needed
- Format amounts consistently
- Handle zero amounts (free tier)

### Caching
- Consider caching pricing data (short TTL, e.g., 5 minutes)
- Invalidate on webhook events (price/product updates)

### Error Handling
- Graceful degradation if Stripe API unavailable
- Fallback to embedded pricing table if custom component fails
- Clear error messages for users

## Migration Strategy

1. **Phase 1**: Deploy backend changes (non-breaking)
2. **Phase 2**: Deploy custom pricing component behind feature flag
3. **Phase 3**: Test with subset of users
4. **Phase 4**: Gradually enable for all users
5. **Phase 5**: Remove embedded pricing table option (optional)

## Success Criteria

1. ✅ Pricing displayed matches Stripe products exactly
2. ✅ No hardcoded pricing values in frontend
3. ✅ Pricing updates automatically when Stripe products change
4. ✅ Custom pricing display works for authenticated users
5. ✅ Public pricing page available (if implemented)
6. ✅ Monitoring/validation in place
7. ✅ Documentation complete

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Stripe API downtime | Fallback to embedded pricing table |
| Pricing mismatch | Validation command + monitoring |
| Breaking changes | Feature flag + gradual rollout |
| Performance issues | Caching + optimization |
| Multiple currencies | Clear currency handling strategy |

## Next Steps

1. Review and approve this plan
2. Prioritize phases based on business needs
3. Start with Phase 1 (Backend API enhancement)
4. Create tickets/tasks for each phase
5. Begin implementation
