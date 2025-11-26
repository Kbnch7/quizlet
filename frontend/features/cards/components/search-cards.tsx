'use client';

import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from '@/components/ui/input-group';
import { Search } from 'lucide-react';

export function SearchCards() {
  return (
    <InputGroup>
      <InputGroupInput placeholder="Search..." />
      <InputGroupAddon align={'inline-end'}>
        <Search />
      </InputGroupAddon>
    </InputGroup>
  );
}
