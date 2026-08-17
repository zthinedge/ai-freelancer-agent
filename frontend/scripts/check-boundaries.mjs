import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { dirname, extname, isAbsolute, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'


const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const sourceRoot = resolve(frontendRoot, 'src')
const layerRank = new Map([
  ['shared', 0],
  ['entities', 1],
  ['features', 2],
  ['pages', 3],
  ['app', 4],
])
const sourceExtensions = new Set(['.ts', '.tsx'])
const importPattern = /(?:from\s+|import\s*\()['"]([^'"]+)['"]/g


function listSourceFiles(directory) {
  return readdirSync(directory).flatMap((name) => {
    const path = resolve(directory, name)
    return statSync(path).isDirectory()
      ? listSourceFiles(path)
      : sourceExtensions.has(extname(path))
        ? [path]
        : []
  })
}


function sourceLocation(path) {
  const parts = relative(sourceRoot, path).split(sep)
  return { layer: parts[0], feature: parts[0] === 'features' ? parts[1] : undefined }
}


function resolveImport(sourcePath, specifier) {
  if (!specifier.startsWith('.')) return undefined
  const candidate = resolve(dirname(sourcePath), specifier)
  const options = [candidate, `${candidate}.ts`, `${candidate}.tsx`, resolve(candidate, 'index.ts')]
  return options.find((path) => existsSync(path))
}


const violations = []
for (const sourcePath of listSourceFiles(sourceRoot)) {
  const source = sourceLocation(sourcePath)
  const content = readFileSync(sourcePath, 'utf8')
  for (const match of content.matchAll(importPattern)) {
    const targetPath = resolveImport(sourcePath, match[1])
    if (!targetPath) continue
    const relativeTarget = relative(sourceRoot, targetPath)
    if (relativeTarget === '..' || relativeTarget.startsWith(`..${sep}`) || isAbsolute(relativeTarget)) {
      continue
    }

    const target = sourceLocation(targetPath)
    const sourceRank = layerRank.get(source.layer)
    const targetRank = layerRank.get(target.layer)
    if (sourceRank === undefined || targetRank === undefined) continue

    if (sourceRank < targetRank) {
      violations.push(`${relative(sourceRoot, sourcePath)} -> ${relative(sourceRoot, targetPath)}`)
    }
    if (
      source.layer === 'features'
      && target.layer === 'features'
      && source.feature !== target.feature
    ) {
      violations.push(`${relative(sourceRoot, sourcePath)} -> cross-feature ${target.feature}`)
    }
  }
}

if (violations.length > 0) {
  console.error('Frontend architecture boundary violations:')
  violations.forEach((violation) => console.error(`- ${violation}`))
  process.exit(1)
}

console.log('Frontend architecture boundaries passed.')
