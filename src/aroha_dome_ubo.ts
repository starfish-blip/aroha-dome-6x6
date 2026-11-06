export interface ArohaResonanceFrame {
  y_vector: [number, number, number, number];
  thermal: {
    raw_temp_c: number;
    delta_t: number;
    freq_hz: number;
    phase_rad: number;
  };
  emergence_entropy_bits: number;
  empirical_validity: number;
  loss: number;
  time_sec: number;
  weights: number[][];
  grad_norm: number;
}

export class ArohaDomeUBOController {
  public static readonly BINDING_POINT = 0;
  public static readonly BLOCK_NAME = "ArohaResonanceUBO";
  public static readonly FLOAT_COUNT = 32;

  private gl: WebGL2RenderingContext;
  private ubo: WebGLBuffer;
  private scratch: Float32Array;

  constructor(gl: WebGL2RenderingContext, program: WebGLProgram) {
    this.gl = gl;
    this.scratch = new Float32Array(ArohaDomeUBOController.FLOAT_COUNT);

    const buffer = gl.createBuffer();
    if (!buffer) {
      throw new Error("Failed to allocate WebGL2 ArohaResonanceUBO buffer.");
    }
    this.ubo = buffer;

    gl.bindBuffer(gl.UNIFORM_BUFFER, this.ubo);
    gl.bufferData(gl.UNIFORM_BUFFER, this.scratch.byteLength, gl.DYNAMIC_DRAW);
    gl.bindBuffer(gl.UNIFORM_BUFFER, null);

    this.bindToProgram(program);
  }

  public bindToProgram(program: WebGLProgram): void {
    const gl = this.gl;
    const blockIndex = gl.getUniformBlockIndex(program, ArohaDomeUBOController.BLOCK_NAME);
    if (blockIndex === gl.INVALID_INDEX) {
      throw new Error(Uniform block '' not found in shader.);
    }

    const byteSize = gl.getActiveUniformBlockParameter(program, blockIndex, gl.UNIFORM_BLOCK_DATA_SIZE);
    if (byteSize !== 128) {
      throw new Error(std140 alignment mismatch: expected 128 bytes, driver reported );
    }

    gl.uniformBlockBinding(program, blockIndex, ArohaDomeUBOController.BINDING_POINT);
    gl.bindBufferBase(gl.UNIFORM_BUFFER, ArohaDomeUBOController.BINDING_POINT, this.ubo);
  }

  public update(frame: ArohaResonanceFrame, displacementGain = 0.12): Float32Array {
    const b = this.scratch;

    b[0] = frame.y_vector[0];
    b[1] = frame.y_vector[1];
    b[2] = frame.y_vector[2];
    b[3] = frame.y_vector[3];

    b[4] = frame.thermal.raw_temp_c;
    b[5] = frame.thermal.delta_t;
    b[6] = frame.thermal.freq_hz;
    b[7] = frame.thermal.phase_rad;

    b[8] = frame.emergence_entropy_bits;
    b[9] = frame.empirical_validity;
    b[10] = frame.loss;
    b[11] = frame.time_sec;

    for (let k = 0; k < 4; k++) {
      const base = 12 + k * 4;
      const row = frame.weights[k];
      const y_k = frame.y_vector[k];
      b[base + 0] = row[0];
      b[base + 1] = row[1];
      b[base + 2] = row[2];
      b[base + 3] = y_k * y_k;
    }

    b[28] = 6.0;
    b[29] = 6.0;
    b[30] = displacementGain;
    b[31] = frame.grad_norm;

    const gl = this.gl;
    gl.bindBuffer(gl.UNIFORM_BUFFER, this.ubo);
    gl.bufferSubData(gl.UNIFORM_BUFFER, 0, b);
    gl.bindBuffer(gl.UNIFORM_BUFFER, null);

    return b;
  }
}
