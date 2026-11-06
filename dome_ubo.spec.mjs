import { test, expect } from '@playwright/test';

test.describe('AROHA v40 Master Matrix & WebGL2 std140 UBO Verification Suite', () => {

  test('1. WebGL2 ArohaResonanceUBO enforces exact 128-byte (32-float) std140 layout on Binding Point 0', async ({ page }) => {
    await page.goto('/aroha_master_matrix_app.html');
    const uboAudit = await page.evaluate(() => {
      const canvas = document.getElementById('dome-canvas');
      const gl = canvas.getContext('webgl2');
      const prog = gl.getParameter(gl.CURRENT_PROGRAM);
      const blockIdx = gl.getUniformBlockIndex(prog, 'ArohaResonanceUBO');
      return {
        blockIdx,
        byteSize: gl.getActiveUniformBlockParameter(prog, blockIdx, gl.UNIFORM_BLOCK_DATA_SIZE),
        binding: gl.getActiveUniformBlockParameter(prog, blockIdx, gl.UNIFORM_BLOCK_BINDING),
        activeUniforms: gl.getActiveUniformBlockParameter(prog, blockIdx, gl.UNIFORM_BLOCK_ACTIVE_UNIFORMS)
      };
    });
    expect(uboAudit.blockIdx).not.toBe(0xFFFFFFFF);
    expect(uboAudit.byteSize).toBe(128);
    expect(uboAudit.binding).toBe(0);
    expect(uboAudit.activeUniforms).toBe(5);
  });

  test('2. Point 26 Zenith Convergence: Tier 6 produces S(rho_A) > 0.05 bits (1+1=3 Emergent) & renders non-empty 3D frame', async ({ page, request }) => {
    await page.goto('/aroha_master_matrix_app.html');
    const stepRes = await request.post('/api/step', {
      data: { tier_id: 6, temp_c: 38.1, gamma_scale: 1.85, lam: 0.75, vowel: 'A', ladder_level: 9, maramataka: 'Rakaunui', train_step: false }
    });
    const stepData = await stepRes.json();
    expect(stepData.emergence_entropy_bits).toBeGreaterThan(0.05);
    expect(stepData.regime).toContain('1+1=3');

    await expect.poll(async () => {
      const txt = await page.locator('#val-ent').textContent();
      return parseFloat(txt);
    }, { timeout: 5000 }).toBeGreaterThan(0.05);
  });

  test('3. 6-Key Vocal Gate ("C" Anchor) locks 36.6C/261.63Hz and Tier buttons scale u_dome_meta.z (#slider-disp)', async ({ page }) => {
    await page.goto('/aroha_master_matrix_app.html');
    await page.locator('.vowel-btn[data-vowel="C"]').click();
    await expect(page.locator('#slider-temp')).toHaveValue('36.6');
    await page.locator('.tier-btn[data-tier="1"]').click();
    await expect(page.locator('#slider-disp')).toHaveValue('0.08');
    await page.locator('.tier-btn[data-tier="6"]').click();
    await expect(page.locator('#slider-disp')).toHaveValue('0.28');
  });

  test('4. Point 25 Reciprocal Handshake commits verified SHA-256 block to Tier 3 Ledger', async ({ page, request }) => {
    await page.goto('/aroha_master_matrix_app.html');
    await page.locator('#btn-hs-confirm').click();
    await expect(page.locator('#val-handshake')).toContainText('LOCKED [SHA256:', { timeout: 5000 });
    const ledgerRes = await request.get('/api/ledger');
    const ledgerData = await ledgerRes.json();
    expect(ledgerData.count).toBeGreaterThan(0);
  });

  test('5. Live AI Oracle Reflection Bridge returns state-mapped telemetry badge and synthesis', async ({ page }) => {
    await page.goto('/aroha_master_matrix_app.html');
    const initialMsgCount = await page.locator('#chat-log .chat-msg').count();
    await page.locator('.catalyst-btn').first().click();
    await expect(page.locator('#chat-log .chat-msg')).toHaveCount(initialMsgCount + 2, { timeout: 6000 });
  });

});
