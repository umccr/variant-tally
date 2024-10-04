#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { VariantTallyStack } from '../lib/variant-tally-stack';

const app = new cdk.App();
new VariantTallyStack(app, 'VariantTallyStack', {
  env: { account: '843407916570', region: 'ap-southeast-2' },
}, { });
