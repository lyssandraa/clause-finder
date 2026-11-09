# Failure examples for manual review

Up to 5 per clause type and approach. Contract-level misses are listed first because a missed clause is the most dangerous error in due diligence. Gold = CUAD lawyer labels.

## Baseline (regex)

### Change of Control

**1. False negative: clause missed entirely (contract level)**  
Contract: `INGEVITYCORP_05_16_2016-EX-10.5-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: > If Parent enters an agreement to transfer the license granted to it under this Section 3.1 in connection with any sale or transfer of a Parent business, then SpinCo and members of the SpinCo Group shall be made third party beneficiaries under such transfer agreement to enforce breaches of the license
- Gold: > If SpinCo enters an agreement to transfer the license granted to it under this Section 3.2 in connection with any sale or transfer of a SpinCo business, then Parent and members of the Parent Group shall be made third party beneficiaries under such transfer agreement to enforce breaches of the license.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `AimmuneTherapeuticsInc_20200205_8-K_EX-10.3_11967170_EX-10.3_Development Agreement`  

- Gold: _(none)_
- Predicted: > Each Party shall have the right to terminate this Agreement upon written notice as a result of the filing or institution of bankruptcy, reorganization, liquidation or receivership proceedings, or upon an assignment of a substantial portion of the assets for the benefit of creditors by the other Party; provided that such termination shall be effective only if such proceeding is not dismissed within ninety (90) days after the filing thereof.
- Predicted: > Neither Party may assign or transfer this Agreement or any rights or obligations hereunder without the prior written consent of the other Party, except that a Party may make such an assignment or transfer without the other Party's written consent to (a) any of its Affiliates, in whole or in part, or (b) any Third Party in connection with (i) the acquisition of such Party by or merger or consolidation of such Party with another entity or (ii) a merger, consolidation, sale of stock, sale of all or substantially all of such Party's assets or other similar transaction in which such Third Party either becomes the owner of all or substantially all of the business and assets of (y) such Party or (z [...]

**3. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT`  

- Gold: _(none)_
- Predicted: > Severance Pay and Benefits Upon Termination by the Company without Cause or by the Executive for Good Reason outside the Change in Control Period.
- Predicted: > 11.7 If your employment is terminated on account of your death or by the Company without Cause (being for any reason not covered by paragraph 11.3), or you terminate your employment for Good Reason (as provided in paragraph 11.4), in either case outside of the Change in Control Period, then the Company shall pay you the Accrued Benefits.
- Predicted: > Severance Pay and Benefits Upon Termination by the Company without Cause or by the Executive for Good Reason Within the Change in Control Period

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `EMERALDHEALTHTHERAPEUTICSINC_06_10_2020-EX-4.5-CONSULTING AGREEMENT - DR. GAETANO MORELLO N.D. INC.`  

- Gold: _(none)_
- Predicted: > (e) "Change of control" means: (i) a person other than the current control person or persons of the Company (as that term is defined in the Securities Act (British Columbia) or other applicable securities legislation) becomes a control person of the Company; or (ii) a majority of the directors elected at any annual or special general meeting of shareholders of Emerald, or by consent resolution, are not individuals nominated by the Company's then-incumbent board.

**5. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `GULFSOUTHMEDICALSUPPLYINC_12_24_1997-EX-4-AFFILIATE AGREEMENT`  

- Gold: _(none)_
- Predicted: > PSS agrees that it will publish such results as promptly as practicable following the Merger in the sole discretion of PSS, but in any event within 45 days after the end of the first fiscal quarter of PSS containing the required period of post-Merger combined operations and that it will notify the undersigned promptly following such publication.

### Anti-Assignment

**1. False negative: clause missed entirely (contract level)**  
Contract: `ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement`  

- Gold: > This Agreement will automatically terminate in the event of its "assignment" (as such term is defined for purposes of Section 15(a) (4) of the Investment Fund Act).
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `ADUROBIOTECH,INC_06_02_2020-EX-10.7-CONSULTING AGREEMENT`  

- Gold: _(none)_
- Predicted: > This Agreement shall not be assignable by Consultant.

**3. False negative: gold span not matched (span level)**  
Contract: `AimmuneTherapeuticsInc_20200205_8-K_EX-10.3_11967170_EX-10.3_Development Agreement`  
Note: closest prediction has Jaccard 0.18  

- Gold: > Any assignment or transfer, or attempted assignment or transfer, by either Party in violation of the terms of this Section 15.6 shall be null and void and of no legal effect.
- Predicted: > provided, however, that to the extent that any agreement or other asset described in this Section 14.2 is not assignable by Aimmune (whether because such agreement or asset is explicitly non-assignable or because the Third Party consent required for such assignment is not obtained), then such agreement or other asset will not be assigned, and upon the request of Xencor, Aimmune will take such steps as may be reasonably necessary to allow Xencor to obtain and to enjoy the benefits of such agreement or other asset.

**4. False positive: predicted span not matched (span level)**  
Contract: `AimmuneTherapeuticsInc_20200205_8-K_EX-10.3_11967170_EX-10.3_Development Agreement`  

- Gold: > Neither Party may assign or transfer this Agreement or any rights or obligations hereunder without the prior written consent of the other Party, except that a Party may make such an assignment or transfer without the other Party's written consent to (a) any of its Affiliates, in whole or in part, or (b) any Third Party in connection with (i) the acquisition of such Party by or merger or consolidation of such Party with another entity or (ii) a merger, consolidation, sale of stock, sale of all or substantially all of such Party's assets or other similar transaction in which such Third Party either becomes the owner of all or substantially all of the business and assets of (y) such Party or (z [...]
- Gold: > Any assignment or transfer, or attempted assignment or transfer, by either Party in violation of the terms of this Section 15.6 shall be null and void and of no legal effect.
- Predicted: > provided, however, that to the extent that any agreement or other asset described in this Section 14.2 is not assignable by Aimmune (whether because such agreement or asset is explicitly non-assignable or because the Third Party consent required for such assignment is not obtained), then such agreement or other asset will not be assigned, and upon the request of Xencor, Aimmune will take such steps as may be reasonably necessary to allow Xencor to obtain and to enjoy the benefits of such agreement or other asset.

**5. False negative: gold span not matched (span level)**  
Contract: `CORIOINC_07_20_2000-EX-10.5-LICENSE AND HOSTING AGREEMENT`  
Note: closest prediction has Jaccard 0.10  

- Gold: > Any assignment in violation of this Section 14.1 shall be null and void.
- Predicted: > Notwithstanding the foregoing, either party shall have the right to assign this Agreement in connection with the merger or acquisition of such party or the sale of all or substantially all of its assets related to this Agreement without such consent, except in the case where such transaction involves a direct competitor of the other party where consent of the other party will be required.

### Termination for Convenience

**1. False negative: clause missed entirely (contract level)**  
Contract: `Freecook_20180605_S-1_EX-10.3_11233807_EX-10.3_Hosting Agreement`  

- Gold: > Company at its sole discretion may at any time alter or cease providing the Customer Service which it has agreed to provide to Client relating to Client Website pursuant to this Agreement without any liability to Company.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `CORIOINC_07_20_2000-EX-10.5-LICENSE AND HOSTING AGREEMENT`  

- Gold: _(none)_
- Predicted: > The following Sections shall survive the termination or expiration of this Agreement for any reason: 4.2, 5.3, 7, 8, 9, 10, 12 and 14.

**3. False negative: clause missed entirely (contract level)**  
Contract: `GAINSCOINC_01_21_2010-EX-10.41-SPONSORSHIP AGREEMENT`  

- Gold: > Notwithstanding the provisions of Section 1 hereof, the Sponsor shall have the right at any time prior to December 31, 2010 to terminate this Agreement by giving written notice of such termination to Racing.
- Predicted: _(not found)_

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `IbioInc_20200313_8-K_EX-10.1_12052678_EX-10.1_Development Agreement`  

- Gold: _(none)_
- Predicted: > 6.3 If either Party to this Agreement fails to perform or violates any material obligation of this Agreement, then, upon thirty (30) days written notice to the breaching Party specifying such failure or violation, the non-breaching Party may terminate this Agreement without liability, unless: (a) the failure or violation specified in the default notice has been cured within the thirty (30) day notice period; or (b) the failure or violation reasonably requires more than thirty (30) days to correct, and the breaching Party has begun substantial corrective action to remedy the failure or violation within the thirty (30) day notice period and diligently pursues such action, in which event, termi [...]

**5. False negative: clause missed entirely (contract level)**  
Contract: `INGEVITYCORP_05_16_2016-EX-10.5-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: > any other Person, including SpinCo.
- Gold: > This Agreement may be terminated at any time prior to the Effective Time by Parent, in its sole and absolute discretion, without the approval or consent of
- Predicted: _(not found)_

### Cap on Liability

**1. False negative: clause missed entirely (contract level)**  
Contract: `CURAEGISTECHNOLOGIES,INC_05_26_2010-EX-1-CORPORATE SPONSORSHIP AGREEMENT`  

- Gold: > Upon termination of this Agreement, NEITHER PARTY SHALL BE LIABLE TO THE OTHER FOR ANY CONSEQUENTIAL, EXEMPLARY, SPECIAL, INCIDENTAL OR PUNITIVE DAMAGES, EVEN IF IT HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES, WHICH ARE RELATED TO THE AGREEMENT OR ITS BREACH.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement`  

- Gold: _(none)_
- Predicted: > Limitation of Liability of the Blockchain Administrator;

**3. False negative: clause missed entirely (contract level)**  
Contract: `HOSPITALITYINVESTORSTRUST,INC_04_07_2014-EX-10.26-FRANCHISE AGREEMENT`  

- Gold: > THE PARTIES ACKNOWLEDGE THAT LIQUIDATED DAMAGES PAYABLE BY YOU UNDER THIS AGREEMENT (WHETHER PRE-OPENING LIQUIDATED DAMAGES OR LIQUIDATED DAMAGES FOR EARLY TERMINATION) ARE NOT PUNITIVE OR EXEMPLARY DAMAGES.
- Predicted: _(not found)_

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `BONTONSTORESINC_04_20_2018-EX-99.3-AGENCY AGREEMENT`  

- Gold: _(none)_
- Predicted: > Until the Designation Rights Termination Date or as otherwise directed by Purchaser or set forth in this Agreement, Merchant shall continue to maintain, subject to the Wind-Down Budget and the Wind-Down Cap, in such amounts as it currently has in effect, all of its liability insurance policies, including but not limited to commercial general liability, products liability, comprehensive public liability, auto liability and umbrella liability insurance, covering injuries to persons and property in, or in connection with, the Assets and/or Merchant's operation of its business and the Store and Distribution Centers; and Merchant shall cause Purchaser to be named as an additional named insured (a [...]

**5. False negative: clause missed entirely (contract level)**  
Contract: `HarpoonTherapeuticsInc_20200312_10-K_EX-10.18_12051356_EX-10.18_Development Agreement`  

- Gold: > EXCEPT (A) FOR FRAUD, WILLFUL MISCONDUCT OR GROSS NEGLIGENCE, (B) FOR A PARTY'S BREACH OF ITS OBLIGATIONS UNDER [ARTICLE 9 OR SECTION 5.8], (C) AS PROVIDED UNDER [***] AND (D) TO THE EXTENT ANY SUCH DAMAGES ARE REQUIRED TO BE PAID TO A THIRD PARTY AS PART OF A CLAIM FOR WHICH A PARTY PROVIDES INDEMNIFICATION UNDER THIS ARTICLE 11, NEITHER PARTY NOR ANY OF ITS AFFILIATES SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES, INCLUDING LOSS OF PROFITS OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, TORT, NEGLIGENCE, BREACH OF STATUTORY DUTY OR OTHERWISE IN CONNECTION WITH OR ARISING IN ANY WAY OUT OF THE TE [...]
- Predicted: _(not found)_

### Non-Compete

**1. False negative: clause missed entirely (contract level)**  
Contract: `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT`  

- Gold: > You hereby agree with the Company that to protect the Company's and any and all Group Company's business interests, customer connections and goodwill and the stability of its or their workforce, that you will not during the Restricted Period (and in respect of sub-paragraph 14.2(f) below only, at any time): (a) in the Restricted Territory, compete with the business of the Company or any Group Company by being directly or indirectly employed or engaged in any capacity by any person, firm or company which engages in or provides Restricted Business or commercial activities competitive with the Restricted Business to Restricted Customers or Prospective Customers; (b) in the Restricted Territory, [...]
- Gold: > (c) in the Restricted Territory, compete with the business of the Company or any Group Company either on your own account or for any person, firm or company directly or indirectly in competition with the Restricted Business by soliciting or endeavouring to solicit or entice the business or custom of any Restricted Customer or Prospective Customer and with whom you personally dealt in respect of Restricted Business in the pursuance of the employment hereunder in the twelve (12) months prior to the Termination Date; (d) either on your own account or for any person, firm or company directly or indirectly solicit or entice away or endeavour to solicit or entice away any director or senior employ [...]
- Gold: > You shall not, without the prior written consent of the Company, either solely or jointly, directly or indirectly, carry on or be engaged, concerned or interested in any other trade or business, including, but not limited to, carrying on business with the Company's suppliers or dealers, save that nothing in this paragraph 13.2 shall prevent you from holding (with the prior written consent of the Company, which shall not be unreasonably delayed or withheld) up to three percent (3%) of the issued equity share capital of any company where those equity shares are listed on a recognised investment exchange (as defined in section 285 of the Financial Services and Markets Act 2000) or traded on the [...]
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `FOUNDATIONMEDICINE,INC_02_02_2015-EX-10.2-Collaboration Agreement`  

- Gold: _(none)_
- Predicted: > Conservatory or interim measures sought by either Party before the Arbitral Tribunal shall not preclude any court of competent jurisdiction granting conservatory or interim measures.

**3. False negative: clause missed entirely (contract level)**  
Contract: `FuelcellEnergyInc_20191106_8-K_EX-10.1_11868007_EX-10.1_Development Agreement`  

- Gold: > During the Term of this Agreement, FCE will not conduct any Work using Generation 1 Technology in Carbon Capture Applications or any Work using Generation 2 Technology, independently or with third parties outside this Agreement, without prior written approval from ExxonMobil.
- Predicted: _(not found)_

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `LOYALTYPOINTINC_11_16_2004-EX-10.2-RESELLER AGREEMENT`  

- Gold: _(none)_
- Predicted: > The non-breaching party shall give the breaching party prompt notice of the non-breaching party's intention to make a claim for indemnification hereunder. the breaching party shall have the opportunity to defend the underlying claims, suit or proceeding by competent counsel of its own choosing, provided that non-breaching party has approved such counsel, which approval shall not be unreasonably withheld.

**5. False negative: clause missed entirely (contract level)**  
Contract: `GAINSCOINC_01_21_2010-EX-10.41-SPONSORSHIP AGREEMENT`  

- Gold: > Subject to payment by the Sponsor of the sponsorship fee provided for herein, during the term of this Agreement Racing shall cause the Racing Team to provide for the Sponsor's benefit all of the benefits customarily associated with the sponsorship of a Daytona Prototype Series racing team and consistent with the benefits provided to the Sponsor in 2005 - 2009 (individually, a "Benefit," and collectively, the "Benefits"), including but not limited to the following:
- Gold: > (v) prohibiting the endorsement by Racing and any members of Racing, including the drivers, of any entities, products or services which are in direct competition or otherwise inconsistent with the Sponsor or it products or services, unless such endorsement activity is approved in writing by Racing and the Sponsor;
- Predicted: _(not found)_

### Governing Law

**1. False negative: clause missed entirely (contract level)**  
Contract: `IMMUNOMEDICSINC_08_07_2019-EX-10.1-PROMOTION AGREEMENT`  

- Gold: > The interpretation, construction and performance of this Agreement, and the rights granted and obligations arising hereunder, shall be governed in accordance with the substantive laws of the State of New York, without regard to its conflicts of law rules.
- Predicted: _(not found)_

**2. False negative: clause missed entirely (contract level)**  
Contract: `RaeSystemsInc_20001114_10-Q_EX-10.57_2631790_EX-10.57_Co-Branding Agreement`  

- Gold: > This Agreement and any action
- Gold: > related thereto shall be governed, controlled, interpreted and defined by and under the laws of the State of California and the United States, without regard to the conflicts of laws provisions thereof.
- Predicted: _(not found)_

**3. False positive: predicted span not matched (span level)**  
Contract: `IdeanomicsInc_20160330_10-K_EX-10.26_9512211_EX-10.26_Content License Agreement`  

- Gold: > This Agreement shall be governed by and construed in all respects in accordance with the laws of the State of New York, without giving effect to any conflicts of laws principles.
- Predicted: > The merits of the dispute shall be resolved in accordance with the laws of the State of New York, without reference to its choice of law rules.

**4. False positive: predicted span not matched (span level)**  
Contract: `ReedsInc_20191113_10-Q_EX-10.4_11888303_EX-10.4_Development Agreement`  

- Gold: > This Agreement shall be governed by, and any dispute arising hereunder shall be determined in accordance with, the laws of State of New York (without giving effect to conflict of laws principles) including all matters of construction, validity and performance.
- Predicted: > To the extent that Company receives any trade secrets of Reed's, Company's obligation to protect such trade secrets and abide by the terms of Section 7 shall survive for so long as such information is a bona fine trade secret pursuant to the laws of the governing jurisdiction identified in Section 14.

**5. False positive: predicted span not matched (span level)**  
Contract: `SoupmanInc_20150814_8-K_EX-10.1_9230148_EX-10.1_Franchise Agreement1`  

- Gold: > This Agreement shall be interpreted and construed under the laws of the State of New York.
- Predicted: > If, however, any provision of this Agreement would not be enforceable under the laws of New York, and if the Franchised Business is located outside of New York and such provision would be enforceable under the laws of the state in which the Franchised Business is located, then such provision shall be interpreted and construed under the laws of that other state.

## LLM

### Change of Control

**1. False negative: clause missed entirely (contract level)**  
Contract: `INGEVITYCORP_05_16_2016-EX-10.5-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: > If Parent enters an agreement to transfer the license granted to it under this Section 3.1 in connection with any sale or transfer of a Parent business, then SpinCo and members of the SpinCo Group shall be made third party beneficiaries under such transfer agreement to enforce breaches of the license
- Gold: > If SpinCo enters an agreement to transfer the license granted to it under this Section 3.2 in connection with any sale or transfer of a SpinCo business, then Parent and members of the Parent Group shall be made third party beneficiaries under such transfer agreement to enforce breaches of the license.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `ARMSTRONGFLOORING,INC_01_07_2019-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: _(none)_
- Predicted: > Either Party may terminate this Agreement if the other Party materially breaches this Agreement and fails to remedy such breach within thirty (30) days' written notice thereof;

**3. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `AimmuneTherapeuticsInc_20200205_8-K_EX-10.3_11967170_EX-10.3_Development Agreement`  

- Gold: _(none)_
- Predicted: > Except as set forth in the immediately preceding sentence, in the event of an assignment or transfer as permitted above in this Section 15.6, the assigning or transferring Party shall remain responsible (jointly and severally) with such Affiliate for the

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT`  

- Gold: _(none)_
- Predicted: > Severance Pay and Benefits Upon Termination by the Company without Cause or by the Executive for Good Reason Within the Change in Control Period
- Predicted: > Change in Control Period. If during the Change in Control Period your employment is terminated on account of your death or by the Company without Cause (being for any reason not covered by paragraph 11.3) or you terminate your employment for Good Reason (as provided in paragraph 11.4), then, subject to (i) your signing (or your authorised representative or estate signing, if the termination is due to your death) a settlement agreement and a separation agreement and release (together the Settlement Agreements) in a form and manner satisfactory to the Company, which shall include, without limitation, a general release of claims against the Company and all related persons and entities, a reaffi [...]
- Predicted: > Schedule Definitions Change in Control: means and includes each of the following: (a) a Sale; or (b) a Takeover.

**5. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `DataCallTechnologies_20060918_SB-2A_EX-10.9_944510_EX-10.9_Content License Agreement`  

- Gold: _(none)_
- Predicted: > Either Party shall be entitled to cancel this Agreement if the other Party is materially in breach of the terms of this Agreement.

### Anti-Assignment

**1. False negative: clause missed entirely (contract level)**  
Contract: `CURAEGISTECHNOLOGIES,INC_05_26_2010-EX-1-CORPORATE SPONSORSHIP AGREEMENT`  

- Gold: > Any attempt to assign without the other party's consent will be null and void and will afford the non-assigning party the right to immediately cancel and terminate this Agreement.
- Gold: > not be unreasonably withheld.
- Gold: > Neither party may assign its rights or powers under this Agreement without the express written consent of the other, which consent shall
- Predicted: _(not found)_

**2. False negative: clause missed entirely (contract level)**  
Contract: `LOGANSROADHOUSEINC_03_27_1998-EX-10.17-SPONSORSHIP AGREEMENT`  

- Gold: > This Agreement may not be modified or assigned except in writing signed by SRP and Logan's.
- Predicted: _(not found)_

**3. False negative: clause missed entirely (contract level)**  
Contract: `PROLONGINTERNATIONALCORP_03_23_1998-EX-10.16-SPONSORSHIP AGREEMENT`  

- Gold: > This Agreement may not be assigned by either party ---------- without the prior written consent of the other party.
- Predicted: _(not found)_

**4. False negative: gold span not matched (span level)**  
Contract: `ARMSTRONGFLOORING,INC_01_07_2019-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT`  
Note: closest prediction has Jaccard 0.40  

- Gold: > Except as otherwise provided in this Agreement, including under Section 7.1, neither this Agreement nor any of the rights, interests or obligations of any Party under this Agreement shall be assigned, in whole or in part, by operation of law or otherwise, by either Party without the prior written consent of the other Party; provided, however, that (a) either Party may assign any of the foregoing in connection with the sale or other transfer of the applicable business or assets of such Party or its Affiliates to which this Agreement relates (except that neither of the Buyer Entities may assign any such rights, interests or obligations with respect to the Arizona Licensed Trademarks); (b) Ariz [...]
- Predicted: > Except as otherwise provided in this Agreement, including under Section 7.1, neither this Agreement nor any of the rights, interests or obligations of any Party under this Agreement shall be assigned, in whole or in part, by operation of law or otherwise, by either Party without the prior written consent of the other Party;

**5. False positive: predicted span not matched (span level)**  
Contract: `ARMSTRONGFLOORING,INC_01_07_2019-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: > Except as otherwise provided in this Agreement, including under Section 7.1, neither this Agreement nor any of the rights, interests or obligations of any Party under this Agreement shall be assigned, in whole or in part, by operation of law or otherwise, by either Party without the prior written consent of the other Party; provided, however, that (a) either Party may assign any of the foregoing in connection with the sale or other transfer of the applicable business or assets of such Party or its Affiliates to which this Agreement relates (except that neither of the Buyer Entities may assign any such rights, interests or obligations with respect to the Arizona Licensed Trademarks); (b) Ariz [...]
- Predicted: > Except as otherwise provided in this Agreement, including under Section 7.1, neither this Agreement nor any of the rights, interests or obligations of any Party under this Agreement shall be assigned, in whole or in part, by operation of law or otherwise, by either Party without the prior written consent of the other Party;

### Termination for Convenience

**1. False negative: clause missed entirely (contract level)**  
Contract: `BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT`  

- Gold: > The Company reserves the right in its sole and absolute discretion to give written notice to
- Gold: > Without prejudice to the Company's right to summarily terminate your employment in accordance with paragraph 11.3 below and your right to summarily terminate your employment for Good Reason in accordance with paragraph 11.4 below, either you or the Company may terminate your employment by giving to the other not less than six months' notice in writing.
- Gold: > terminate your employment forthwith and to make a payment to you in lieu of salary and the benefits set out in paragraph 5 of this Agreement for all or any unexpired part of the notice period.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement`  

- Gold: _(none)_
- Predicted: > This Agreement may be terminated at any time, without the payment of any penalty, upon 60 days' written notice, by the vote of a majority of the outstanding voting securities of the Fund or by the vote of the Fund's Trustees or by the Blockchain Administrator.

**3. False negative: clause missed entirely (contract level)**  
Contract: `BONTONSTORESINC_04_20_2018-EX-99.3-AGENCY AGREEMENT`  

- Gold: > Subject to the Wind-Down Budget and payment of Expenses, Agent shall use the E-Commerce Platform in connection with the GOB Sale to fulfill customer orders made during the GOB Sale Term and otherwise promote the GOB Sale (in Agent's capacity as Agent hereunder), provided that Agent shall have the option, in its sole discretion, to terminate the use of the E-Commerce Platform at any time after four weeks of use.
- Predicted: _(not found)_

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `HYDRONTECHNOLOGIESINC_03_31_1997-EX-10.47-SPONSORSHIP AGREEMENT`  

- Gold: _(none)_
- Predicted: > Hydron shall have the right to terminate this Agreement upon written notice to Dolphins at any time between November 1, 1997 and December 15, 1997, in which event this Agreement shall be terminated following the Dolphins last 1997 regular or post-season game, if any.

**5. False negative: clause missed entirely (contract level)**  
Contract: `Freecook_20180605_S-1_EX-10.3_11233807_EX-10.3_Hosting Agreement`  

- Gold: > Company at its sole discretion may at any time alter or cease providing the Customer Service which it has agreed to provide to Client relating to Client Website pursuant to this Agreement without any liability to Company.
- Predicted: _(not found)_

### Cap on Liability

**1. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement`  

- Gold: _(none)_
- Predicted: > The Blockchain Administrator (and its officers, managers, partners, agents, employees, controlling persons, members and any other person or entity affiliated with the Blockchain Administrator) shall not be liable to the Fund for any action taken or omitted to be taken by the Blockchain Administrator in connection with the performance of any of its duties or obligations under this Agreement or otherwise as blockchain administrator of the Fund, and the Fund shall indemnify, defend and protect the Blockchain Administrator (and its officers, managers, partners, agents, employees, controlling persons, members and any other person or entity affiliated with the Blockchain Administrator) (collective [...]

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `BONTONSTORESINC_04_20_2018-EX-99.3-AGENCY AGREEMENT`  

- Gold: _(none)_
- Predicted: > Purchaser shall not be liable for any claims against Merchant except as expressly provided for in this Agreement;
- Predicted: > Any portion of the Wind-Down Payment that has not been expended by Merchant as of the Designation Rights Termination Date shall revert and be returned to Purchaser upon the dismissal or conversion of Merchant's chapter 11 bankruptcy cases or the effective date of a plan of liquidation of Merchant.
- Predicted: > Purchaser shall have no obligation to investigate, assess, object to, or contest the merits of any 503(b)(9) Claims or Stub Rent Claims and is entitled to rely on the amounts included on such reconciliation.

**3. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `HYDRONTECHNOLOGIESINC_03_31_1997-EX-10.47-SPONSORSHIP AGREEMENT`  

- Gold: _(none)_
- Predicted: > In the event that the consideration is not paid by Hydron on or before the applicable payment due date, said failure to pay shall be considered a material breach by Hydron, and the Dolphins may elect to charge Hydron a late fee of 1.5% per month of the payment then due and owing until it is paid in full.
- Predicted: > The Dolphins agree to provide written notice to Hydron of the failure to receive any payment, and Hydron shall have a five (5) business day period following delivery of written notice in which to cure the payment default before the Dolphins may elect to terminate this Agreement and pursue applicable remedies.

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `INGEVITYCORP_05_16_2016-EX-10.5-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: _(none)_
- Predicted: > the remainder shall be allocated to the Enforcing Party.
- Predicted: > The rights and obligations of the Parties under Section 6.4 (Record Retention), Section 6.5 (Limitation of Liability), Section 6.6 (Other Agreements Providing for Exchange of Information), Section 6.7 (Production of Witnesses; Records; Cooperation), Section 6.8 (Privileged Matters), Section 6.9 (Confidentiality), and Section 6.10 (Protective Arrangements) of the Separation Agreement are hereby incorporated into this Section 5 as if fully set forth herein.
- Predicted: > To the extent (a) Parent, or any member of the Parent Group, receives from SpinCo, or any member of the SpinCo Group, or (b) SpinCo, or any member of the SpinCo Group receives from Parent, or any member of the Parent Group, any Information that is trade secret under applicable law, the five (5) year confidentiality period of Section 6.9(a) of the Separation Agreement with respect to such Information shall be extended until such time as the received Information is no longer trade secret.

**5. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `PROFOUNDMEDICALCORP_08_29_2019-EX-4.5-SUPPLY AGREEMENT`  

- Gold: _(none)_
- Predicted: > The limitations and exclusions set forth above in this clause 10 shall apply to the fullest extent permitted by applicable Law.

### Non-Compete

**1. False negative: clause missed entirely (contract level)**  
Contract: `LOGANSROADHOUSEINC_03_27_1998-EX-10.17-SPONSORSHIP AGREEMENT`  

- Gold: > Furthermore, SRP shall not permit any associate or secondary sponsor to suggest in any manner that its sponsorship role is as great as that of Logan's.
- Gold: > The Driver shall not drive for any other sponsor which competes with Logan's.
- Gold: > SRP may not obtain any associate or secondary sponsors whose products or concepts compete with Logan's.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `ADUROBIOTECH,INC_06_02_2020-EX-10.7-CONSULTING AGREEMENT`  

- Gold: _(none)_
- Predicted: > From the Effective Date and for twelve (12) months after the termination of this Agreement (the "Restricted Period"), Consultant shall not, without Aduro's prior written consent, directly or indirectly, solicit or encourage any employee or contractor of Aduro or its affiliates to terminate employment with, or cease providing Services to, Aduro or its affiliates.

**3. False negative: clause missed entirely (contract level)**  
Contract: `RaeSystemsInc_20001114_10-Q_EX-10.57_2631790_EX-10.57_Co-Branding Agreement`  

- Gold: > The spinwares and spinstore will be modified to include licensed content purchased directly from Spinrecords.com and to eliminate products that will compete with the Nettaxi store.
- Predicted: _(not found)_

**4. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `EMERALDHEALTHTHERAPEUTICSINC_06_10_2020-EX-4.5-CONSULTING AGREEMENT - DR. GAETANO MORELLO N.D. INC.`  

- Gold: _(none)_
- Predicted: > The Contractor's performance of personal, business or charitable activities or service on any boards of any private or public companies, shall be deemed not to be preventing the Contractor from meeting his or her obligations to Emerald hereunder, so long as same are not directly competitive with the business of the Company.

**5. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `FOUNDATIONMEDICINE,INC_02_02_2015-EX-10.2-Collaboration Agreement`  

- Gold: _(none)_
- Predicted: > Except for Excepted Activities, for the lesser of (i) […***…] after the Effective Date or (ii) […***…] (the "Immunotherapy Exclusivity Period"), FMI will work exclusively with Roche with respect to […***…]. Except with regard to Excepted Activities, FMI will not (i) work directly or indirectly with any Third Party in the field of […***…], (ii) use for the benefit of any Third Party the […***…] or (iii) transfer to or otherwise enable any Third Party to make use of any data, technology or results from the Immunotherapy Testing Platform Development Program for […***…].

### Governing Law

**1. False negative: clause missed entirely (contract level)**  
Contract: `ENTRUSTINC_07_24_1998-EX-10.5-STRATEGIC ALLIANCE AGREEMENT`  

- Gold: > This Agreement shall be governed by and be --------- ---- construed in accordance with the laws of the Province of Ontario, Canada.
- Predicted: _(not found)_

**2. False positive: clause reported but not in the gold labels (contract level)**  
Contract: `INGEVITYCORP_05_16_2016-EX-10.5-INTELLECTUAL PROPERTY AGREEMENT`  

- Gold: _(none)_
- Predicted: > the U.S. Bankruptcy Code (the "Code") and any similar laws in any other country,
- Predicted: > The terms and conditions set forth in Section 10.2 (Governing Law) through Section 10.19 (Mutual Drafting) of the Separation Agreement are hereby incorporated into this Section 8 as if fully set forth herein.

**3. False negative: clause missed entirely (contract level)**  
Contract: `PROLONGINTERNATIONALCORP_03_23_1998-EX-10.16-SPONSORSHIP AGREEMENT`  

- Gold: > This Agreement shall be ------------------------------------- governed by and construed in accordance with the substantive laws of the State of North Carolina.
- Predicted: _(not found)_

**4. False negative: clause missed entirely (contract level)**  
Contract: `RaeSystemsInc_20001114_10-Q_EX-10.57_2631790_EX-10.57_Co-Branding Agreement`  

- Gold: > This Agreement and any action
- Gold: > related thereto shall be governed, controlled, interpreted and defined by and under the laws of the State of California and the United States, without regard to the conflicts of laws provisions thereof.
- Predicted: _(not found)_

**5. False negative: gold span not matched (span level)**  
Contract: `ARMSTRONGFLOORING,INC_01_07_2019-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT`  
Note: closest prediction has Jaccard 0.88  

- Gold: > This Assignment shall be governed by the laws of the State of Delaware, its rules of conflict of laws notwithstanding.
- Predicted: > This Agreement shall be governed by the laws of the State of Delaware, its rules of conflict of laws notwithstanding.
